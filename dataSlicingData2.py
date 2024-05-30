import pandas as pd

# Load the CSV file
data = pd.read_csv('NSDUH_2022_Tab.txt', delimiter='\t')
#print("Unique values before replacement:", data['SMIPY'].unique())
#print("Unique values before replacement:", data['AMIPY'].unique())
# data preprocessing
data['SMIPY'] = data['SMIPY'].fillna('-7')
data['SMIPY'] = data['SMIPY'].astype(int)
data['AMIPY'] = data['AMIPY'].fillna('-7')
data['AMIPY'] = data['AMIPY'].astype(int)
#print("Unique values after replacement:", data['SMIPY'].unique())
#print("Unique values after replacement:", data['AMIPY'].unique())

# Load the data dictionary
data_dictionary = pd.read_csv('DataDictionary_SelectedData_2_NSDUH_2022.csv') 
# data preprocessing
#print("Unique values before replacement:", data_dictionary['Answer_code'].unique())
data_dictionary['Answer_code'] = data_dictionary['Answer_code'].replace('.', '-3')
data_dictionary['Answer_code'] = data_dictionary['Answer_code'].fillna('-4')
data_dictionary['Answer_code'] = data_dictionary['Answer_code'].astype(int)
#print("Unique values after replacement:", data_dictionary['Answer_code'].unique())
answer_name = data_dictionary['Answer_name']
answer_meaning = data_dictionary['Answer_meaning']


def apply_mapping(column_name, data_series):
    # Filter the data dictionary for the current column
    dict_subset = data_dictionary[data_dictionary['Question_code'] == column_name]
    if dict_subset.empty:
        #print(f"No mapping found for column: {column_name}")
        return data_series  # If no mapping is found, return the original series

    # Initialize a result series with 'Unknown' to handle unmapped values
    result_series = pd.Series('Unknown', index=data_series.index)

    for index, row in dict_subset.iterrows():
        answer_type = row['Answer_type']
        #print(f"Processing row: {row.to_dict()}")
        
        if answer_type == 'direct':
            try:
                start_range = int(row['Answer_code'])
                end_range = int(row['Answer_name'])
                #print(f"Direct mapping from {start_range} to {end_range}")
                mask = data_series.between(start_range, end_range, inclusive='both')
                result_series[mask] = data_series[mask].apply(lambda x: str(int(x)))  # Convert directly to string of int
            except ValueError as e:
                #print(f"Error in direct mapping: {e}")
                continue
        elif answer_type == 'optional':
            mapping_dict = {(int(float(key))): val for key, val in zip(dict_subset['Answer_code'], dict_subset['Answer_meaning'])} #since previous conversion is int, these are strings
            #print(f"Optional mapping dictionary: {mapping_dict}") #works
            # Print the data series before mapping
            #print(f"Data series before mapping: {data_series.head()}") #works
            unknown_mask = result_series == 'Unknown'
            #print(f"Result Series: {result_series.head()}")
            # Ensure data series values are strings for mapping
            #data_series_str = data_series.astype(str)
            mapped_values = data_series[unknown_mask].map(mapping_dict)
            # Print the mapped values
            #print(f"Mapped values: {mapped_values.head()}") #somewhere before here it breaks
            result_series[unknown_mask] = mapped_values.fillna('Unknown')

    #print(f"Final mapped series: {result_series.head()}")
    return result_series

def apply_name_mapping(column_name, data_series):
    # Filter the data dictionary for the current column
    dict_subset = data_dictionary[data_dictionary['Question_code'] == column_name]
    if dict_subset.empty:
        #print(f"No name mapping found for column: {column_name}")
        return data_series  # If no mapping is found, return the original series

    # Initialize a result series with 'Unknown' to handle unmapped values
    results_series = pd.Series('Unknown', index=data_series.index)

    for index, row in dict_subset.iterrows():
        answer_type = row['Answer_type']
        #print(f"Processing row: {row.to_dict()}")
        
        if answer_type == 'direct':
            try:
                start_range = int(row['Answer_code'])
                end_range = int(row['Answer_name'])
                #print(f"Direct name mapping from {start_range} to {end_range}")
                mask = data_series.between(start_range, end_range, inclusive='both')
                results_series[mask] = data_series[mask].apply(lambda x: str(int(x)))  # Convert directly to string of int
            except ValueError as e:
                #print(f"Error in direct name mapping: {e}")
                continue
        elif answer_type == 'optional':
            mapping_dictname = {(int(float(key))): val for key, val in zip(dict_subset['Answer_code'], dict_subset['Answer_name'])}
            #print(f"Optional name mapping dictionary: {mapping_dictname}")
            # Print the data series before mapping
            #print(f"Data series before name mapping: {data_series.head()}")
            # Print the data types of data_series and mapping_dictname keys
            #print(f"Data series types: {data_series.dtypes}")
            #print(f"Mapping dictname keys types: {[type(k) for k in mapping_dictname.keys()]}")
            unknown_mask2 = results_series == 'Unknown'
            # Ensure data series values are strings for mapping
            #data_series_str2 = data_series.astype(str)
            mappedname_values = data_series[unknown_mask2].map(mapping_dictname)
            # Print the mapped name values
            #print(f"Mapped name values: {mappedname_values.head()}")
            results_series[unknown_mask2] = mappedname_values.fillna('Unknown')

    #print(f"Final name mapped series: {results_series.head()}")
    return results_series



# Function to create data frames for each substance #the issue is that i only have the one question with multiple possible answers
def create_information_data(question_code_column, question_code):
    #data[data[question_code_column]] = data[data[question_code_column]].fillna(-1)
    #data[data[question_code_column]] = data[data[question_code_column]].replace('.', '0')
        # Ensure the column is of integer type
    #data[data[question_code_column]] = data[data[question_code_column]].astype(int)
    filtered_data = data[data[question_code_column] != -7] #| data[data[question_code_column] == 1]

    # Debugging output
    #print(f"Filtered Data: {filtered_data[[question_code_column, 'QUESTID2']].head()}")

    # Create the information data DataFrame
    information_data = pd.DataFrame()
    information_data['PersonID'] = filtered_data['QUESTID2']
    
    if question_code:
        information_data['Question'] = apply_name_mapping(question_code, filtered_data[question_code])
        information_data['Answer'] = apply_mapping(question_code, filtered_data[question_code]) 
    else:
        information_data['Question'] = ' '
        information_data['Answer'] = ' '
    #what if the names were hardcoded?

    #if the answer value is equal to something, also add what it means
    
    # Debugging output
    print(f"Information Data: {information_data.head()}")
    return information_data

# Create data frames for each substance
appended_SMIR_data = create_information_data('SMIPY','SMIRSUD5ANY')
appended_SMI_data = create_information_data('SMIPY','SMISUD5ANYO')
appended_AMIR_data = create_information_data('AMIPY','AMIRSUD5ANY')
appended_AMI_data = create_information_data('AMIPY','AMISUD5ANYO')

# Combine data frames
combined_data = pd.concat([appended_SMIR_data, appended_SMI_data, appended_AMIR_data, appended_AMI_data], ignore_index=True)
# Save the combined data to CSV
combined_data.to_csv('AppendedData2.csv', header=True, index=False)

print("Data has been successfully appended to AppendedData2.csv.")
