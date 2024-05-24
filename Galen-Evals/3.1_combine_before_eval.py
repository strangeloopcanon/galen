# Combine files before Eval
import os
import pandas as pd
from config import config

F_NAME = config.F_NAME
# File paths
db_file_path = f'files/{F_NAME}_results_grouped_by_question_db.xlsx'
dynamic_file_path = f'files/{F_NAME}_results_grouped_by_question_dynamic.xlsx'
rag_file_path = f'files/{F_NAME}_results_grouped_by_question_rag.xlsx'

# Load the Excel files if they exist
db_df = pd.read_excel(db_file_path) if os.path.exists(db_file_path) else pd.DataFrame()
dynamic_df = pd.read_excel(dynamic_file_path) if os.path.exists(dynamic_file_path) else pd.DataFrame()
rag_df = pd.read_excel(rag_file_path) if os.path.exists(rag_file_path) else pd.DataFrame()

# Selecting only the relevant columns
relevant_columns = ['Question', 'Model', 'Response', 'Latency', 'Category', 'Type']

# Filter the columns if dataframes are not empty
db_selected = db_df[relevant_columns] if not db_df.empty else pd.DataFrame(columns=relevant_columns)
dynamic_selected = dynamic_df[relevant_columns] if not dynamic_df.empty else pd.DataFrame(columns=relevant_columns)
rag_selected = rag_df[relevant_columns] if not rag_df.empty else pd.DataFrame(columns=relevant_columns)

def normalize_questions(df):
    df_copy = df.copy()
    df_copy.loc[:, 'Question'] = df_copy['Question'].str.lower().str.strip()
    return df_copy

# Normalize questions if dataframes are not empty
db_df = normalize_questions(db_selected) if not db_selected.empty else pd.DataFrame(columns=relevant_columns)
dynamic_df = normalize_questions(dynamic_selected) if not dynamic_selected.empty else pd.DataFrame(columns=relevant_columns)
rag_df = normalize_questions(rag_selected) if not rag_selected.empty else pd.DataFrame(columns=relevant_columns)

# Combining the selected DataFrames
combined_df = pd.concat([db_df, dynamic_df, rag_df], ignore_index=True)
# Fill missing 'Response' values right after concatenation
combined_df['Response'].fillna('No response', inplace=True)
combined_df['Category'].fillna('No category', inplace=True)
# Removing duplicates
final_combined_df = combined_df.drop_duplicates(subset=['Question', 'Model', 'Category', 'Type'])

# Save the cleaned and combined DataFrame to a new Excel file
output_file_path = f'files/{F_NAME}_allresults_combined.xlsx'
combined_df.to_excel(output_file_path, index=False)

print(f"Combined file saved to: {output_file_path}")

# Step 1: Ensure consistent "Category" for each "Question"
combined_df['Category'] = combined_df.groupby('Question')['Category'].transform('first')
# Check for missing values in key columns
missing_values_check = combined_df[['Question', 'Model', 'Response']].isnull().sum()
print("Missing values check:\n", missing_values_check)

# Pivot the DataFrame
pivot_df = combined_df.pivot_table(index=['Question', 'Category'], columns='Model', values='Response', aggfunc=lambda x: ' | '.join(x.dropna().unique())).reset_index()

# Clean up the DataFrame for saving
pivot_df.reset_index(drop=True, inplace=True)
pivot_df.columns.name = None  # Remove the index/columns level name for a cleaner output

output_pivot_file_path = f'files/{F_NAME}_combined_questions_responses.xlsx'
pivot_df.to_excel(output_pivot_file_path, index=False)

print(f"Pivoted file saved to: {output_pivot_file_path}")
