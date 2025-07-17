import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

df_purged_final = pd.read_excel("df_purged.xlsx")

# Create a copy of the original dataset to modify it
df_modified = df_purged_final.copy()

# Replace the values of 0 in 'avg_frequency' with 0.01
df_modified['avg_frequency'] = df_modified['avg_frequency'].replace(0, 0.01)

# %%
# # Color palette for each unique value in the 'codigo' column
# unique_codes = df_modified['codigo'].unique()
# palette = sns.color_palette("Spectral", len(unique_codes))  # You can change the palette if you prefer other colors
# color_map_final = dict(zip(unique_codes, palette))  # Assign a color to each value of 'codigo'

# Group codes under the same color
color_group_map = {
    'Group 1': ['mt', 'msr', 'mfsa', 'mps', 'tmf', 'mr'],
    'Group 2': ['mfb', 'mffb'],  
    'Group 3': ['mh', 'ihn'],             
    'Group 4': ['mff', 'mm', 'pm', 'mfh', 'mix']           
}

# Manually assign colors to each group
color_map_grouped = {
    'Group 1': 'blue',
    'Group 2': 'green',
    'Group 3': 'red',
    'Group 4': 'orange'
}

# Create a new color mapping where the same color is assigned to all codes in a group
color_map_final = {}
for group, codes in color_group_map.items():
    for code in codes:
        color_map_final[code] = color_map_grouped[group]  # Assign the same color to all codes in the group

# Apply jittering to the points with avg_frequency = 0.01
jitter_strength = 0.005  # Adjust the jittering size
df_modified_jittered = df_modified.copy()
df_modified_jittered.loc[df_modified_jittered['avg_frequency'] == 0.01, 'avg_frequency'] += np.random.uniform(-jitter_strength, jitter_strength, df_modified_jittered[df_modified_jittered['avg_frequency'] == 0.01].shape[0])

# Create the plot
plt.figure(figsize=(6, 5))

# Create the plot with points, assigning color by 'codigo' column
sns.scatterplot(
    data=df_modified_jittered, 
    x='avg_frequency', 
    y='Year', 
    hue='codigo',  # Color by the 'codigo' column
    palette=color_map_final,  # Use the color mapping
    alpha=0.7,
    s=60,  # Size of the points
    zorder=1  # Ensure points are in front of the bars
)

# Add author labels only for points that meet the citedby threshold
citedby_threshold = 10000  

for i in range(len(df_modified_jittered)):
    if df_modified_jittered['citedby_count'][i] >= citedby_threshold:
        plt.text(
            df_modified_jittered['avg_frequency'][i], 
            df_modified_jittered['Year'][i], 
            df_modified_jittered['creator'][i], 
            fontsize=14,
            fontweight='bold',
            ha='center',
            va='bottom'
        )

# Log scale for x axis
plt.xscale('log')
plt.ylim(1990, 2026)

# Add axis labels and title
plt.xlabel('Frequency (Hz)')
plt.ylabel('Year')
#plt.title('Magnetic Field Frequencies')

# # Show the legend of colors for 'codigo'
# plt.legend(title='Code', loc='upper right', bbox_to_anchor=(1.22, 1))

# Create the grouped manual legend
legend_elements = [
    Patch(facecolor='blue', edgecolor='blue', label='Group 1: specific physics'),
    Patch(facecolor='green', edgecolor='green', label='Group 2: hydrogel biomaterials'),
    Patch(facecolor='red', edgecolor='red', label='Group 3: hyperthermia'),
    Patch(facecolor='orange', edgecolor='orange', label='Group 4: general physics')
]

# Add the custom legend to the plot
plt.legend(handles=legend_elements, title='Groups', loc='center left', bbox_to_anchor=(0.18, 1.18))

# Show the plot
plt.show()

# %%
# Create a histogram of the frequencies, with the frequencies on the x-axis and the number of papers on the y-axis
# Bins for the histogram must be in log scale and range from 1e-1 to 1e12
# Each bin must be a decade wide

# Create the plot
plt.figure(figsize=(6, 4))

# Create the histogram
sns.histplot(
    data=df_purged_final, 
    x='avg_frequency', 
    bins=np.logspace(-1, 11, num=13),  # 23 bins from 1e-1 to 1e12
    color='skyblue',  # Color of the bars
    edgecolor='black',  # Color of the edges of the bars
    alpha=0.7  # Transparency of the bars
)

# Log scale for x axis
plt.xscale('log')

# Log scale for y axis
#plt.yscale('log')

# Add axis labels and title
plt.xlabel('Frequency (Hz)', fontsize=14)
plt.ylabel('Number of Papers', fontsize=14)
plt.title('Magnetic Field Frequencies Histogram', fontsize=14)

# Show the plot and save it to a file
#plt.tight_layout()
#plt.savefig('magnetic_field_frequencies_histogram.png')
plt.show()

# %%
# Separate zero and non-zero values
zero_values = df_purged_final[df_purged_final['avg_frequency'] == 0]
non_zero_values = df_purged_final[df_purged_final['avg_frequency'] > 0]

# Create the plot
plt.figure(figsize=(6, 4))

# Plot the zero values as a separate bar
plt.bar(0.48, len(zero_values), width=1, color='lightcoral', edgecolor='black', alpha=0.7, label='Static')

# Create the histogram for non-zero values
sns.histplot(
    data=non_zero_values, 
    x='avg_frequency', 
    bins=np.logspace(0, 11, num=12),  # 23 bins from 1e-1 to 1e12
    color='skyblue',  # Color of the bars
    edgecolor='black',  # Color of the edges of the bars
    alpha=0.7,  # Transparency of the bars
    label='Dynamic'
)

# Log scale for x axis
plt.xscale('log')
plt.xlim(1.01e-1, 1e8)

# Add axis labels and title
plt.xlabel('Frequency (Hz)', fontsize=14)
plt.ylabel('Number of Papers', fontsize=14)
plt.title('Magnetic Field Frequencies Histogram', fontsize=14)
plt.legend()

# Show the plot and save it to a file
# plt.tight_layout()
# plt.savefig('magnetic_field_frequencies_histogram.png')
plt.show()
# %%

# Count the number of papers with frequencies in the range of 101 Hz to 10 kHz

# Filter the DataFrame to get the papers with frequencies in the desired range
freq_range = df_purged_final[(df_purged_final['avg_frequency'] >= 101) & (df_purged_final['avg_frequency'] <= 10e3)]

# Count the number of papers in the range
num_papers = len(freq_range)
# Total number of papers
total_papers = len(df_purged_final)

print('Papers in range 100-10000 Hz:', num_papers)
print('Percentage of papers in our range:', num_papers / total_papers * 100)

# Count the number of papers with frequencies in the range of 101 Hz to 1 kHz

# Filter the DataFrame to get the papers with frequencies in the desired range
freq_range = df_purged_final[(df_purged_final['avg_frequency'] >= 101) & (df_purged_final['avg_frequency'] <= 1e3)]

# Count the number of papers in the range
num_papers = len(freq_range)
# Total number of papers
total_papers = len(df_purged_final)

print('Papers in range 100-1000 Hz:', num_papers)
print('Percentage of papers in our range:', num_papers / total_papers * 100)


