import pandas as pd
import os
import re

def extract_keywords(text):
    if pd.isna(text):
        return ""

    if text == "No keywords":
        return ""
    
    # Find all matches of the pattern "'$': '([^']*)'"
    matches = re.findall(r"\$': '([^']*)'", text)

    # Join the matches with a comma and space
    keywords_clean = ', '.join(matches)
    return keywords_clean

# Path to the folder containing the files
folder_path = ".//Data"
# Path to the output folder
output_path = ".//Data//db_final"
# Get the list of .xlsx files in the folder
file_list = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]

# Read and concatenate all .xlsx files
df_list = [pd.read_excel(os.path.join(folder_path, file)) for file in file_list]
df = pd.concat(df_list, ignore_index=True)

# Convert the 'cover_date' column to datetime format and 'citedby_count' to numeric
df['cover_date'] = pd.to_datetime(df['cover_date'], errors='coerce')
df['citedby_count'] = pd.to_numeric(df['citedby_count'], errors='coerce')

# Create a new column 'Year' by extracting the year from 'cover_date'
df['Year'] = df['cover_date'].dt.year

# Identify duplicates based on the 'title' column
duplicated_titles = df[df.duplicated(subset=['title'], keep=False)]

# Change the value of 'codigo' to 'mix' for duplicates
df.loc[df['title'].isin(duplicated_titles['title']), 'codigo'] = 'mix'

# Remove duplicates, keeping only one row per 'title'
df = df.drop_duplicates(subset=['title'], keep='first')

# Clean up keywords
df['keywords_clean'] = df['keywords'].apply(extract_keywords)

# Save the result to a new Excel file
df.to_excel(os.path.join(output_path, 'db_merg.xlsx'), index=False)
