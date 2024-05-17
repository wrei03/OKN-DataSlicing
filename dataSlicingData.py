import pandas as pd

# Load the TSV file
data = pd.read_csv('NSDUH_2022_Tab.txt', delimiter='\t')

# Load the data dictionary
data_dictionary = pd.read_csv('DataDictionary_SelectedData_NSDUH2022.csv') 
answer_name = data_dictionary['Answer_name']
answer_meaning = data_dictionary['Answer_meaning']

# Load the substances data
substances = pd.read_csv('substance.csv')


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
def create_substance_data(substance_name, substance_code_column, recency_question): #substance_code_column, withinthirtydays, withinyear, overyear): #potentially need an withinthreeyears
    filtered_data = data[data[substance_code_column] == 1] #modified #[data[substance_code_column] == 1] #has to do with something here as to why it's not directly pulling from the answer meaning column
    substance_row = substances[substances['SubstanceName'] == substance_name]
    substance_id = substance_row['SubstanceID'].iloc[0]
    
    substance_data = pd.DataFrame()
    substance_data['PersonID'] = filtered_data['QUESTID2']
    substance_data['SubstanceID'] = substance_id
    #substance_data['DaysConsumedPast30Days'] = apply_mapping(days_column, filtered_data[days_column])
    #substance_data['? Unknown'] = apply_mapping(recency_question, filtered_data[recency_question])
    if recency_question:
        substance_data['Question'] = apply_name_mapping(recency_question, filtered_data[recency_question])
        substance_data['Answer'] = apply_mapping(recency_question, filtered_data[recency_question]) #filtered_data[recency_question])
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
consumes_cigs_data = create_substance_data('Cigarettes', 'CIGEVER', 'IRCIGRC')
consumes_cigar_data = create_substance_data('Cigar', 'CIGAREVR', 'IRCGRRC')
consumes_pipe_data = create_substance_data('Pipe', 'PIPEVER','IRPIPLF')
consumes_nicvp_data = create_substance_data('Nicotine Vape', 'NICVAPEVER', 'IRNICVAPREC')
consumes_smkless_data = create_substance_data('Smokeless Tobacco', 'SMKLSSEVR', 'IRSMKLSSREC')
consumes_alcohol_data = create_substance_data('Alcohol', 'ALCEVER', 'IRALCRC')
consumes_cbdhmp_data = create_substance_data('CBD/Hemp', 'CBDHMPEVR', 'IRCBDHMPREC')
consumes_mj_data = create_substance_data('Marijuana', 'MJEVER', 'IRMJRC')
consumes_cocaine_data = create_substance_data('Cocaine', 'COCEVER', 'IRCOCRC')
consumes_crack_data = create_substance_data('Crack', 'CRKEVER', 'IRCRKRC')
consumes_heroine_data = create_substance_data('Heroine', 'HEREVER', 'IRHERRC')
consumes_hallu_data = create_substance_data('Hallucinogen', 'HALLUCEVR', 'IRHALLUCREC')
consumes_lsd_data = create_substance_data('LSD', 'LSD', 'IRLSDRC')
consumes_pcp_data = create_substance_data('PCP', 'PCP', 'IRPCPRC')
consumes_ecstasy_data = create_substance_data('Ecstasy', 'ECSTMOLLY', 'IRECSTMOREC')
consumes_ketamine_data = create_substance_data('Ketamine', 'KETMINESK','IRKETMINREC')
consumes_damtfx_data = create_substance_data('DMT/AMT/FOXY', 'DMTAMTFXY', 'IRDAMTFXREC')
consumes_salvia_data = create_substance_data('Salvia', 'SALVIADIV', 'IRSALVIAREC')
consumes_inhalant_data = create_substance_data('Inhalant','INHALEVER', 'IRINHALREC')
consumes_meth_data = create_substance_data('Methamphetamine', 'METHAMEVR', 'IRMETHAMREC')





# Combine data frames
combined_data = pd.concat([consumes_cigs_data, consumes_cigar_data, consumes_pipe_data, consumes_nicvp_data, consumes_smkless_data, consumes_alcohol_data, consumes_cbdhmp_data, consumes_mj_data, consumes_cocaine_data, consumes_crack_data,consumes_heroine_data, consumes_hallu_data, consumes_lsd_data, consumes_pcp_data, consumes_ecstasy_data, consumes_ketamine_data, consumes_damtfx_data, consumes_salvia_data, consumes_inhalant_data, consumes_meth_data], ignore_index=True)
# Save the combined data to CSV
combined_data.to_csv('consumes.csv', header=True, index=False)

print("Data has been successfully appended to consumes.csv.")