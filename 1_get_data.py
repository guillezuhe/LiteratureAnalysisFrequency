"XXXXXXXXXXXXXXXXXXX IMPORTS XXXXXXXXXXXXXXXXXXXXXX"
import requests
import pandas as pd
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry  # To handle retries

"XXXXXXXXXXXXXXXXXXX FUNCTIONS XXXXXXXXXXXXXXXXXXXXXX"
# Configure retries
def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,  # Maximum number of retries
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,  # Incremental factor in pause between retries
        status_forcelist=status_forcelist,  # List of status codes that trigger a retry
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Function to get the article details, including the abstract
def get_article_abstract(scopus_id, retry_fail_count):
    url_1 = f'https://api.elsevier.com/content/abstract/scopus_id/{scopus_id}'
    headers = {
        'Accept': 'application/json',
        'X-ELS-APIKey': API_KEY
    }
    try:
        response = requests_retry_session().get(url_1, headers=headers)
        if response.status_code == 200:
            return response.json(), retry_fail_count  # Return data and failure count
        else:
            print(f"Error fetching abstract for Scopus ID {scopus_id}: {response.status_code}")
            return None, retry_fail_count  # Ensure to return None and counter
    except requests.exceptions.RequestException as e:
        retry_fail_count += 1  # Increment counter when retries are exceeded
        print(f"Failed to fetch abstract after retries for Scopus ID {scopus_id}: {e}")
        return None, retry_fail_count

# Function to get the article's keywords
def get_article_keywords(scopus_id, retry_fail_count):
    url_2 = f'https://api.elsevier.com/content/abstract/scopus_id/{scopus_id}?field=authkeywords'
    headers = {
        'Accept': 'application/json',
        'X-ELS-APIKey': API_KEY
    }
    try:
        response = requests_retry_session().get(url_2, headers=headers)
        if response.status_code == 200:
            return response.json(), retry_fail_count  # Return data and failure count
        else:
            print(f"Error fetching keywords for Scopus ID {scopus_id}: {response.status_code}")
            return None, retry_fail_count  # Ensure to return None and counter
    except requests.exceptions.RequestException as e:
        retry_fail_count += 1  # Increment counter when retries are exceeded
        print(f"Failed to fetch keywords after retries for Scopus ID {scopus_id}: {e}")
        return None, retry_fail_count

"XXXXXXXXXXXXXXXXXXX GET DATA XXXXXXXXXXXXXXXXXXXXXX"
API_KEY = "xxxxxxxxxx"  # Replace with your Scopus API key
query = 'TITLE("magnetic hyperthermia") OR KEY("magnetic hyperthermia") OR ABS("magnetic hyperthermia")'
url_p = "https://api.elsevier.com/content/search/scopus"

# Step 2: Set headers and request parameters
headers = {
    "X-ELS-APIKey": API_KEY
}

params = {
    "query": query,
    "count": 25,  # Number of results per page (maximum 25)
    "start": 0   # Index of the first result
}

# Set the maximum number of results to download
max_results = 4000  # Adjust this value as needed
total_downloaded = 0
request_count = 0  # Request counter to apply pause
retry_fail_count = 0  # Retry failure counter

articles = []

# Step 3: Make requests to the API and handle pagination
while total_downloaded < max_results:
    try:
        response = requests_retry_session().get(url_p, headers=headers, params=params)
        data = response.json()
    except requests.exceptions.RequestException as e:
        retry_fail_count += 1  # Increment counter when retries are exceeded
        print(f"Failed to fetch data after retries: {e}")
        break

    if 'search-results' in data and 'entry' in data['search-results']:
        entries = data['search-results']['entry']
        articles.extend(entries)
        total_downloaded += len(entries)
        request_count += 1  # Increment request counter
        
        # Check if maximum number of results has been reached
        if total_downloaded >= max_results:
            break
        
        # Prepare the next request by incrementing the start index
        params["start"] += params["count"]
        
        # If fewer results are received than requested, exit the loop
        if len(entries) < params["count"]:
            break
        
        # Pause every 200 requests
        if request_count % 25 == 0:
            print("Sleeping for 5 seconds to avoid hitting rate limits...")
            time.sleep(5)  # 5-second pause to avoid overloading the API
    else:
        break

# Limit articles to the specified maximum amount
articles = articles[:max_results]

# Step 4: Process and store data
article_data = []
details_request_count = 0  # Counter for detail requests

for article in articles:
    scopus_id = article.get('dc:identifier', '').split(':')[-1]
    title = article.get('dc:title', 'No title')
    creator = article.get('dc:creator', 'No creator')
    publication_name = article.get('prism:publicationName', 'No publication name')
    cover_date = article.get('prism:coverDate', 'No cover date')

    # Get article details, including the abstract
    details, retry_fail_count = get_article_abstract(scopus_id, retry_fail_count)
    details_request_count += 1  # Increment detail request counter
    
    if details:
        coredata = details.get('abstracts-retrieval-response', {}).get('coredata', {})
        abstract = coredata.get('dc:description', 'No abstract')
        cited_by_count = coredata.get('citedby-count', 'No citedby count')
    else:
        abstract = 'No abstract'
        cited_by_count = 'No citedby count'
    
    # Pause every 200 detail requests
    if details_request_count % 25 == 0:
        print("Sleeping for 5 seconds to avoid hitting rate limits (details)...")
        time.sleep(5)  # 5-second pause to avoid overloading the API in the detail step

    # Get article keywords
    keywords_details, retry_fail_count = get_article_keywords(scopus_id, retry_fail_count)
    details_request_count += 1  # Increment detail request counter
    
    if keywords_details:
        keywords = keywords_details.get('abstracts-retrieval-response', {}).get('authkeywords', 'No keywords')
    else:
        keywords = 'No keywords'

    article_data.append({
        'title': title,
        'creator': creator,
        'publication_name': publication_name,
        'cover_date': cover_date,
        'abstract': abstract,
        'keywords': keywords,
        'citedby_count': cited_by_count
    })
    
    # Pause every 200 detail requests
    if details_request_count % 25 == 0:
        print("Sleeping for 5 seconds to avoid hitting rate limits (keywords)...")
        time.sleep(5)  # 5-second pause to avoid overloading the API in the keyword step

# At the end of the process, you can print or use the retry failure count:
print(f"Total failed requests due to retry limit exceeded: {retry_fail_count}")
#%%
# Create a pandas DataFrame and display the data
df = pd.DataFrame(article_data)

# Assign a value to the new column 'code'
code_value = "mh"  # Replace this value with what you want related to the search
df['code'] = code_value

print(df)

#%%
#Save data
datasave_path = (".//Data")
df.to_csv(".//Data//articles_db_mh.csv", index=False)
df.to_excel(".//Data//articles_db_mh.xlsx", index=False)

