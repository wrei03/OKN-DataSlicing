import pandas as pd

# Load the TSV file
data = pd.read_csv('NSDUH_2022_Tab.txt', delimiter='\t')

# Load the data dictionary
data_dictionary = pd.read_csv('DataDictionary_SelectedData_3_NSDUH2022.csv') 
answer_name = data_dictionary['Answer_name']
answer_meaning = data_dictionary['Answer_meaning']

# Load the substances data
substances = pd.read_csv('substance3.csv')


def apply_mapping(column_name, data_series): #data_series): #going to have to fix this
    # Filter the data dictionary for the current column
    dict_subset = data_dictionary[data_dictionary['Question_code'] == column_name]
    if dict_subset.empty:
        return data_series # If no mapping is found, return the original series

    # Initialize a result series with 'Unknown' to handle unmapped values
    result_series = pd.Series('Unknown', index=data_series.index)

    for index, row in dict_subset.iterrows():
        answer_type = row['Answer_type']
        if answer_type == 'direct':
            try:
                start_range = int(row['Answer_code'])
                end_range = int(row['Answer_name'])
                mask = data_series.between(start_range, end_range, inclusive='both')
                result_series[mask] = data_series[mask].apply(lambda x: str(int(x)))  # Convert directly to string of int
            except ValueError:
                continue
        elif answer_type == 'optional':
            '''         
            try:
                start_range = int(row['Answer_code'])
                end_range = int(row['Answer_name'])
            '''
            # Convert and map only 'Unknown' values
            #wouldn't we need to map the ones that aren't unknown?
            #result_series = data_series.apply(lambda x: answer_meaning.get(x, 'Unknown'))
                                              #str(x) if pd.notnull(x) else 'Unknown')
            mapping_dict = {str(int(float(key))): val for key, val in zip(dict_subset['Answer_code'], dict_subset['Answer_meaning'])}
            unknown_mask = result_series == 'Unknown'
            mapped_values = data_series[unknown_mask].astype(str).map(mapping_dict)
            result_series[unknown_mask] = mapped_values.fillna('Unknown')

    return result_series

def apply_name_mapping(column_name, data_series):
    # Filter the data dictionary for the current column
    dict_subset = data_dictionary[data_dictionary['Question_code'] == column_name]
    if dict_subset.empty:
        return data_series # If no mapping is found, return the original series

    # Initialize a result series with 'Unknown' to handle unmapped values
    results_series = pd.Series('Unknown', index=data_series.index)

    for index, row in dict_subset.iterrows():
        answer_type = row['Answer_type']
        if answer_type == 'direct':
            try:
                start_range = int(row['Answer_code'])
                end_range = int(row['Answer_name'])
                mask = data_series.between(start_range, end_range, inclusive='both')
                results_series[mask] = data_series[mask].apply(lambda x: str(int(x)))  # Convert directly to string of int
            except ValueError:
                continue
        elif answer_type == 'optional':
            '''         
            try:
                start_range = int(row['Answer_code'])
                end_range = int(row['Answer_name'])
            '''
            # Convert and map only 'Unknown' values
            #wouldn't we need to map the ones that aren't unknown?
            #result_series = data_series.apply(lambda x: answer_meaning.get(x, 'Unknown'))
                                              #str(x) if pd.notnull(x) else 'Unknown')
            mapping_dictname = {str(int(float(key))): val for key, val in zip(dict_subset['Answer_code'], dict_subset['Answer_name'])}
            unknown_mask2 = results_series == 'Unknown'
            mappedname_values = data_series[unknown_mask2].astype(str).map(mapping_dictname)
            results_series[unknown_mask2] = mappedname_values.fillna('Unknown')

    return results_series

# Function to create data frames for each substance #the issue is that i only have the one question with multiple possible answers
def create_substance_data(substance_name, substance_code_column, year_question): #substance_code_column, withinthirtydays, withinyear, overyear): #potentially need an withinthreeyears
    filtered_data = data[data[substance_code_column] == 1] #modified #[data[substance_code_column] == 1] #has to do with something here as to why it's not directly pulling from the answer meaning column
    substance_row = substances[substances['SubstanceName'] == substance_name]
    substance_id = substance_row['SubstanceID'].iloc[0]
    
    substance_data = pd.DataFrame()
    substance_data['PersonID'] = filtered_data['QUESTID2']
    substance_data['SubstanceID'] = substance_id
    #substance_data['DaysConsumedPast30Days'] = apply_mapping(days_column, filtered_data[days_column])
    #substance_data['? Unknown'] = apply_mapping(year_question, filtered_data[year_question])
    if year_question:
        substance_data['Question'] = apply_name_mapping(year_question, filtered_data[year_question])
        substance_data['Answer'] = apply_mapping(year_question, filtered_data[year_question]) #filtered_data[recency_question])
        #substance_data['Answer Name'] = apply_mapping (filtered_data[recency_question], answer_name)
        #substance_data['Answer Meaning'] = apply_mapping (filtered_data[recency_question], answer_meaning)
    else:
        substance_data['Question'] = ' '
        substance_data['Answer'] = ' '
        #substance_data['Answer Name'] = ' '
        #substance_data['Answer Meaning'] = ' '
    #what if the names were hardcoded?

    #if the answer value is equal to something, also add what it means
    
    return substance_data

# Create data frames for each substance
alcohol_data = create_substance_data('Alcohol', 'ALCEVER', 'ALCYDAYS')
mj_data = create_substance_data('Marijuana', 'MJEVER', 'MRJYDAYS')
cocaine_data = create_substance_data('Cocaine', 'COCEVER', 'COCYDAYS')
crack_data = create_substance_data('Crack', 'CRKEVER', 'CRKYDAYS')
heroine_data = create_substance_data('Heroine', 'HEREVER', 'HERYDAYS')
hallu_data = create_substance_data('Hallucinogen', 'HALLUCEVR', 'HALLNDAYYR')
inhalant_data = create_substance_data('Inhalant','INHALEVER', 'INHNDAYYR')
meth_data = create_substance_data('Methamphetamine', 'METHAMEVR', 'METHNDAYYR')





# Combine data frames
combined_data = pd.concat([alcohol_data, mj_data, cocaine_data, crack_data, heroine_data, hallu_data, inhalant_data, meth_data], ignore_index=True)
# Save the combined data to CSV
combined_data.to_csv('AppendedData3.csv', header=True, index=False)

print("Data has been successfully appended to AppendedData3.csv.")