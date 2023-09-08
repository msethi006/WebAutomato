import pandas as pd
import re
import openai
import os
import ast
import argparse

def openAI_api_call(content):
    completion = openai.ChatCompletion.create(
    model = 'gpt-4',
    messages = [
        {'role': 'user', 'content': content}
    ],
    temperature = 0.9  
    )
    response = completion['choices'][0]['message']['content']
    return response

def get_matching_columns_name(column_name,matching_columns):
    content = f"Map this columns name [{column_name}] to the template columns: [{', '.join(matching_columns)}].Give same exact column name as in template columns list .Just Give single output complete column name nothing else. Try to return the first column name that matches"
    completion = openai.ChatCompletion.create(
  model = 'gpt-4',
  messages = [
    {'role': 'user', 'content': content}
  ],
  temperature = 0.9  
)
    response = completion['choices'][0]['message']['content']
    return response.strip()
def clean_string(input_string):
    return re.sub(r'[^a-zA-Z0-9]', '', input_string)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process CSV files with GPT-4')
    parser.add_argument('--source', help='Path to the source. A CSV file')
    parser.add_argument('--template', help='Path to the template. A CSV file')
    parser.add_argument('--target', help='Path to the target. A CSV file')
    args = parser.parse_args()
    with open(os.path.join(os.getcwd(), "OpenAIAPI.txt"),'r') as file:
        api_key = file.read()
        openai.api_key = api_key

    template_df = pd.read_csv(args.template)
    table_A_df = pd.read_csv(args.template)
    template_df_columns = list(template_df.columns)
    table_A_df_columns = list(table_A_df.columns)

    template_df_columns = list(template_df.columns)
    table_A_df_columns = list(table_A_df.columns)
    # Mapping of column names from table A to the template
    template_column_to_input_columns = {}

    # Iterate through table A columns
    for column_A in template_df_columns:
        # Find the best matching column name in the template using GPT-4
        best_match = get_matching_columns_name(column_A, table_A_df_columns)
        template_column_to_input_columns[column_A] = best_match
    template_column_to_input_columns

    target_df = pd.DataFrame(columns = [list(template_df.columns)])
    numeric_columns = template_df.select_dtypes(include=['int', 'float']).columns
    total_columns = list(template_df.columns)
    for current_column in numeric_columns:
        target_df[current_column] = table_A_df[template_column_to_input_columns[current_column]]
        target_df[current_column] = target_df[current_column].astype(template_df[current_column].dtype)
        total_columns.remove(current_column)
    # Add Date Logic here
    content = f"Just return column name, without quotes, which most matches with Date {total_columns}."
    date_response = openAI_api_call(content)
    content = f"Input date is {template_df[date_response].iloc[0]} whose format is Date/Month/Year. 2nd Date is {table_A_df[template_column_to_input_columns[date_response]].iloc[0]}. Give the python date format for 2nd Date. Only give date format string in output"
    date_format_response = openAI_api_call(content)
    date_format_response= date_format_response.strip('"')
    target_df[date_response] = pd.to_datetime(table_A_df[template_column_to_input_columns[date_response]],format= date_format_response).dt.strftime('%d-%m-%Y')
    total_columns.remove(date_response)
    # Handling Policy Number
    content = f"Just return column name, without quotes, which most matches with Policy Number {total_columns}."
    policy_num_response = openAI_api_call(content)
    if table_A_df[template_column_to_input_columns[policy_num_response]].iloc[0].isalnum() == False:
        target_df[policy_num_response] = table_A_df[template_column_to_input_columns[policy_num_response]].map(clean_string)
    total_columns.remove(policy_num_response)
    # Handling Policy Plan Name
    content = f"Just return column name, without quotes, which most matches with Plan {total_columns}."
    plan_name_response = openAI_api_call(content)
    content = f"Just give dictionary to map [{list(table_A_df[template_column_to_input_columns[plan_name_response]].unique())} to [{list(template_df[plan_name_response].unique())}]]. Dont't add any \n"
    plane_name_mapping_dict = ast.literal_eval(openAI_api_call(content))
    target_df[plan_name_response] = table_A_df[template_column_to_input_columns[plan_name_response]].map(plane_name_mapping_dict)
    total_columns.remove(plan_name_response)
    content = f"Just return column name, without quotes, which most matches with Employe Name {total_columns}."
    name_response = openAI_api_call(content)
    target_df[name_response] = table_A_df[template_column_to_input_columns[name_response]]
    total_columns.remove(name_response)
    target_df.to_csv(args.target,index=False)
