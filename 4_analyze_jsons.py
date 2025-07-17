import pandas as pd
import re
import os
import numpy as np

# Load the json files
jsons_path = "jsons/"

# Initialize an empty DataFrame with the desired column types
df = pd.DataFrame(columns=['index', 'title', 'frequency', 'justification', 'num_frequency'])

# Iterate over the json files
# Get the number of json files in the folder
jsons = os.listdir(jsons_path)
jsons = [f for f in jsons if f.endswith('.json')]

Nones = []

for i in range(len(jsons)):
    print('Paper: ', i)
    # Load the json file
    with open(jsons_path+str(i)+'.json', 'r', encoding='ISO-8859-1') as f:
        data = f.read()
    # Close the file
    f.close()
    
    # Extract the frequency and justification
    frequency = re.search(r'"frequency": "(.*?)"', data).group(1)
    justification = re.search(r'"justification": "(.*?)"', data).group(1)
    title = re.search(r'"title": "(.*?)"', data).group(1)
    
    pattern = re.compile(r'\b(\d+(?:\.\d+)?)\s*(Hz|kHz|MHz|GHz)\b', re.IGNORECASE)
    frequencies = pattern.findall(frequency)
    
    # First check if the frequency is 0
    if frequency == '0':
        num_freq = [0.0]
    # Then check if it is Nan or nan
    elif frequency.lower() == 'nan':
        num_freq = [np.nan]
    # Then look for all the units expressions (Hz, kHz, MHz, GHz) and look for the numbers right before them (with or without a space in between)
    elif len(frequencies) > 0:
        # Convert the frequencies to Hertz (don't use the function convert_to_hz)
        num_freq = []
        for freq in frequencies:
            value, unit = freq
            value = float(value)
            unit = unit.lower()
            if unit == 'hz':
                num_freq.append(value)
            elif unit == 'khz':
                num_freq.append(value * 1e3)
            elif unit == 'mhz':
                num_freq.append(value * 1e6)
            elif unit == 'ghz':
                num_freq.append(value * 1e9)
    # Then look for all the units expressions (Hz, kHz, MHz, GHz) but no numbers before them, and set the value to 1 multiplied by the corresponding factor
    elif re.search(r'\b(Hz|kHz|MHz|GHz)\b', frequency, re.IGNORECASE):
        unit = re.search(r'\b(Hz|kHz|MHz|GHz)\b', frequency, re.IGNORECASE).group(1).lower()
        if unit == 'hz':
            num_freq = [1.0]
        elif unit == 'khz':
            num_freq = [1.0 * 1e3]
        elif unit == 'mhz':
            num_freq = [1.0 * 1e6]
        elif unit == 'ghz':
            num_freq = [1.0 * 1e9]
    # Else return None
    else:
        num_freq = None
        Nones.append(i)

    # Ensure num_freq is a single value or a list with a single element
    if num_freq is None:
        num_freq = [None]
    elif isinstance(num_freq, list) and len(num_freq) == 0:
        num_freq = [None]

    # Average the frequencies if there are multiple
    if len(num_freq) > 1:
        avg_freq = [sum(num_freq) / len(num_freq)]
    else:
        avg_freq = num_freq
    
    # Look if "range" is in the frequency string
    if 'range' in frequency.lower():
        print('Range found in frequency string:', frequency, '. Attributed value:', num_freq)

    # Create a DataFrame with the extracted information
    df_temp = pd.DataFrame({
        'index': [i], 
        'title': [title], 
        'frequency': [frequency], 
        'justification': [justification], 
        'num_frequency': [num_freq],
        'avg_frequency': [avg_freq]
    })
    
    # Append the DataFrame to the main DataFrame
    df = pd.concat([df, df_temp], ignore_index=True)

# Save the Nones to a file with int values
np.savetxt('.//jsons//Nones.txt', Nones, fmt='%i')


# Read the df_merg.xlsx file. It contains the same papers as the df_analyzed_frequencies.xlsx file, but with more columns with extra information
df_expanded = pd.read_excel('.//Data//db_final//db_merg.xlsx')

# Merge the two DataFrames, with df_expanded as the left DataFrame and df as the right DataFrame, but remove the 'index' and 'title' column from df
df_purged = pd.merge(df_expanded, df.drop(columns=['index', 'title']), left_index=True, right_index=True)

# Delete the rows with NaN or None values in the 'avg_frequency' column
df_purged = df_purged.dropna(subset=['avg_frequency'])

# Convert the 'avg_frequency' column to a numeric type. They are currently lists with a single element
df_purged['avg_frequency'] = df_purged['avg_frequency'].apply(lambda x: x[0])

# Remove the rows with Missing values in the 'avg_frequency' column
df_purged = df_purged.dropna(subset=['avg_frequency'])

# Save the DataFrame to an Excel file
df_purged.to_excel('df_purged.xlsx', index=False)
