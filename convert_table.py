import pandas as pd
import re
import openai
import os
import ast
import argparse


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
    table_A_df = pd.read_csv(args.source)
    template_df_data = template_df.values.tolist()
    template_df_data.insert(0,list(template_df.columns))
    table_A_df_data = table_A_df.values.tolist()
    table_A_df_data.insert(0,list(table_A_df.columns))
    content = f"I am giving sample values from 2 CSV Files. Template Table {template_df_data}. Table A {table_A_df_data}. Output a dictionary which maps column names of Template Table to Table A. Output should only contain python dictionary nothing else. No code"
    completion = openai.ChatCompletion.create(
    model = 'gpt-4',#'gpt-3.5-turbo', #gpt-4
    messages = [
            {'role': 'user', 'content': content}
        ],
        temperature = 0.9  
    )
    response1 = completion['choices'][0]['message']['content']
    column_mapping = ast.literal_eval(response1)
    table_A_df_data  = table_A_df[list(column_mapping.values())].values.tolist()
    table_A_df_data.insert(0,list( table_A_df[list(column_mapping.values())].columns))
    content = f"I am giving sample values from 2 CSV Files. Template Table {template_df_data}. Table A {table_A_df_data}. This dictionary maps Template Table to Table A {column_mapping}. Go through values of mapped colums.For columns where value formatting is different, Output a dictionary which maps unique values of Table A to Template Table. The key of dictionary should be column name and value is dictionary which maps values. No Code, No Text."
    completion = openai.ChatCompletion.create(
    model = 'gpt-4',#'gpt-3.5-turbo', #gpt-4
    messages = [
            {'role': 'user', 'content': content}
        ],
        temperature = 0.9  
        )
    response2 = completion['choices'][0]['message']['content']
    response2_dict = ast.literal_eval(response2)
    target_df = pd.DataFrame(columns = [list(template_df.columns)])
    for column in list(column_mapping.keys()):
        if column_mapping[column] not in list(response2_dict.keys()):
            target_df[column] = table_A_df[column_mapping[column]]
    for column in list(column_mapping.keys()):
        if column_mapping[column] in list(response2_dict.keys()):
            target_df[column] = table_A_df[column_mapping[column]].map(response2_dict[column_mapping[column]])


    target_df.to_csv(args.target,index=False)
