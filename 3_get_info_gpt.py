from openai import OpenAI
import pandas as pd

client = OpenAI()

def get_abstract_info(title, abstract, keywords):
    prompt = '''I am going to give you the title, abstract and keywords (when available) of a scientific paper, where a magnetic field is applied. I want to know the range of frequencies of the applied magnetic fields in the work. Based on the application or any implicit message, return an estimate of the range of frequencies employed. Avoid excessively wide ranges and try to keep the interval as specific as possible. If it is possible to give just one representative value instead of a range, do it. 
## Steps
1.	Read the title, abstract and keywords to obtain a general comprehension of the work.
2.	Look for key sentences where frequency clues can be obtained.
3.	Identify the frequency range or the most representative frequency in the study. If the field is presumably static return 0 and if there is no clear clue, please return Nan.
4.	Analyze the context and justification for using these frequencies based on the application, paying attention to why they are crucial for the study.
5.	Organize the information found and write a concise explanation about the use of the frequencies, following the output format and example.
## Output format
The output format should be a JSON that includes:
-	“frequency”: The frequency range or specific frequency used. If it is a range, separate the values by commas.
-	“justification”: A brief explanation of the use of these frequencies in the study.
#### Output example
```json
{
 	"frequency": "50 Hz, 200 Hz", 
  "justification": "The study focuses its analysis on this range because it represents the frequencies that most affect sound transmission in aquatic environments."
 }
```
## Notes
-	 Ensure that the justifications are specific and directly related to the information in the paper.
-    Express the frequency with their units and STRICTLY RESPECT THE OUTPUT FORMAT IN THE EXAMPLE. IN CASE YOU FIND AN APPROPRIATE FREQUENCY VALUE OR RANGE, THE "frequency" ITEM MUST BE ALWAYS AT LEAST A NUMERICAL VALUE, SEPARATED BY A SPACE TO THE UNITS. IN THE CASE OF A RANGE, YOU MUST WRITE A COMMA AND THEN THE LAST VALUE OF THE RANGE IN THE SAME FORMAT.
## Input text:

'''
    prompt += "Title: "+ str(title) + "\n\n" + "Abstract: " + str(abstract) + "\n\n" + "Keywords: " + str(keywords)
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Load the dataframe in the excel file
df_expanded_path = ".//Data//db_final//db_merg.xlsx"
df_expanded = pd.read_excel(df_expanded_path)

# Delete all the columns except the 'title', 'abstract' and 'keywords' columns
df_expanded = df_expanded[['title', 'abstract', 'keywords_clean']]

# Analyze the first ten rows of the dataframe
for i in range(len(df_expanded)):
    print('Analyzing article ', i, '. Title: ', df_expanded['title'][i])
    title = df_expanded['title'][i]
    abstract = df_expanded['abstract'][i]
    keywords = df_expanded['keywords_clean'][i]
    output = get_abstract_info(title, abstract, keywords)
    #print(output)
    # Save the raw output in a txt file
    with open('jsons/outputs_raw/'+str(i)+'.txt', 'w', encoding='utf-8') as f:
        f.write(output)
    # Close the file
    f.close()

    # #%%
    # Remove the initial ```json and ``` from the output. Export everything between {} to a json file
    # Include the brackets in the output
    output_2 = output[output.find("```json")+8:output.rfind("```")]

    # Insert the title in the output as a third key after the frequency and justification keys
    output_3 = output_2[:output_2.rfind("}")-1]+',\n  "title": "'+title+'"\n}'
    print(output_3)

    # Save the output in a json file
    with open('jsons/'+str(i)+'.json', 'w', encoding='utf-8') as f:
        f.write(output_3)
    # Close the file
    f.close()
