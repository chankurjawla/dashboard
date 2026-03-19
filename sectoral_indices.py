import pdfplumber
import pandas as pd
import os

all_tables_pdfplumber = []
source_folder = './indice_pdfs/'

def extract_tables_from_pdf(pdf_path):
    # Reset all_tables_pdfplumber for each call to avoid accumulating tables
    # or better, make it local to the function
    current_pdf_tables = []

    file_name = pdf_path.split('/')[-1]
    month_name = file_name.replace('.pdf', '').split('_')[-1]
    print(month_name)

    with pdfplumber.open(pdf_path) as pdf: # Fix: Use pdf_path instead of global selected_pdf_file
        for page_num, page in enumerate(pdf.pages):
            # Extract tables from the page
            page_tables = page.extract_tables()
            for table_data in page_tables:
                # Convert list of lists to DataFrame, assuming the first row is header
                if table_data and len(table_data) > 1: # Ensure there's header and at least one row of data
                    df = pd.DataFrame(table_data[1:], columns=table_data[0])
                    current_pdf_tables.append(df)
                elif table_data and len(table_data) == 1: # Handle tables with only a header row
                    df = pd.DataFrame(columns=table_data[0])
                    current_pdf_tables.append(df)

    print(f"Extracted {len(current_pdf_tables)} potential tables using pdfplumber from {pdf_path}.")

    # Assuming the relevant table is the first one extracted from the current PDF.
    # If the structure is always similar, this should correctly select the main table.
    if not current_pdf_tables:
        print(f"No tables extracted from {pdf_path}. Returning empty DataFrame.")
        return pd.DataFrame()

    df = current_pdf_tables[0].copy()

    # Find the starting and ending indices for filtering
    start_index = df[df['Index Name'].str.contains('Sectoral Indices', na=False)].index
    end_index = df[df['Index Name'].str.contains('Strategy Indices', na=False)].index

    if not start_index.empty and not end_index.empty:
        start_idx = start_index[0]
        end_idx = end_index[0]
        sectoral_strategy_df = df.loc[start_idx+1 : end_idx-1].copy()
    else:
        print("Could not find 'Sectoral Indices' or 'Strategy Indices' in the 'Index Name' column of the selected table.")
        print("Please inspect the 'Index Name' column of the extracted tables for exact wording.")
        return pd.DataFrame() # Return empty if markers not found

    # Select only the first two columns (Index Name and the first metric, as identified visually)
    # and rename the second column to the extracted month_name.
    sectoral_strategy = sectoral_strategy_df.iloc[:, [0, 1]].copy() # Select first two columns
    sectoral_strategy.columns = ['Months', f'{month_name}'] # Rename to suit transposed matrix

    # Transpose for better display where months become columns and indices become rows
    sectoral_strategy_transposed = sectoral_strategy.transpose()
    sectoral_strategy_transposed.columns = sectoral_strategy_transposed.iloc[0]
    sectoral_strategy_transposed = sectoral_strategy_transposed.iloc[1:]

    # Reset the index to make 'Months' a regular column for merging
    sectoral_strategy_transposed = sectoral_strategy_transposed.reset_index(names=['Months'])

    return sectoral_strategy_transposed

def get_sectoral_indices():
    df_list = []
    i = 0
    for filename in os.listdir(source_folder):
      if filename.endswith('.pdf'):
        file_path = os.path.join(source_folder, filename)
        table = extract_tables_from_pdf(file_path)
        if not table.empty:
            df_list.append(table.copy()) # Append the DataFrame directly to the list
        i += 1

    sectoral_strategy = pd.concat(df_list, ignore_index=True) # combine all the tables
    sectoral_strategy['Months_dt'] = pd.to_datetime(sectoral_strategy['Months'], format='%b%Y')
    sectoral_strategy_sorted = sectoral_strategy.sort_values(by='Months_dt', ascending=False).reset_index(drop=True)
    sectoral_strategy_sorted = sectoral_strategy_sorted.drop(columns=['Months_dt'])
    return sectoral_strategy_sorted











