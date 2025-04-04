# 1. read api http://10.23.141.247:8010/summary/overall and get the data
# 2. then, extract from the data and get two dataframe

import requests
import pandas as pd
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAI



def process_nccl_pie_data(json_data_list):
    """
    Process NCCL JSON data into a pandas DataFrame with single-level columns using pandas operations

    Args:
        json_data_list (list): List of JSON data containing NCCL performance metrics

    Returns:
        pandas.DataFrame: Processed data with columns [config, name, count, range, value]
    """
    # Create a list of tuples containing (config, data_list) for each item
    config_data_pairs = [(item['config'], pd.DataFrame(item['data'])) for item in json_data_list]

    # Create and concatenate DataFrames with their respective configs
    dfs = [df.assign(config=config) for config, df in config_data_pairs]

    # Concatenate all DataFrames efficiently
    result_df = pd.concat(dfs, ignore_index=True)

    # Reorder columns to put config first
    result_df = result_df[['config', 'name', 'count', 'range', 'value']]

    return result_df


def fetch_and_process_nccl_summary():
    """
    Fetches NCCL summary data from API and processes it into dataframes

    Returns:
        tuple: Two pandas DataFrames containing processed NCCL summary data
    """
    # 1. Read API data
    api_url = "http://10.23.141.247:8010/summary/overall?nccl_version=2.24"
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
    except requests.RequestException as e:
        print(f"Error fetching API data: {e}")
        return None, None

    # 2. Process data into dataframes
    try:
        dimensions_data = data['data']["source"]
        df1 = pd.DataFrame(dimensions_data)

        pie_data = data['pie_data']
        df2 = process_nccl_pie_data(pie_data)

        return df1, df2
    except Exception as e:
        print(f"Error processing data into dataframes: {e}")
        return None, None

if __name__ == "__main__":
    # Initialize ChatOpenAI client with local deepseek model
    # Using localhost:7869 as the base URL for the API
    # No API key needed for local deployment
    # Using deepseek-r1 70B model with temperature=0 for consistent outputs
    client = ChatOpenAI(
        base_url="http://localhost:7869/v1",
        api_key="no-need",
        model="deepseek-r1:70b",
        temperature=0
    )

    df1, df2 = fetch_and_process_nccl_summary()
    if df1 is not None and df2 is not None:
        print("DataFrame 1:", df1.head())
        print("DataFrame 2:", df2.head())

    agent = create_pandas_dataframe_agent(
        client,
        df1,
        verbose=True,
        allow_dangerous_code=True,
        handle_parsing_errors=True,
        max_iterations=3,

    )

    # response =agent.invoke("What is the shape of the dataframe?")
    # print("Response:", response)

    response =agent.invoke("Please give me the top 10 questions to ask for both the dataframes to let users understand the data clearly and concisely?")
    print("Response:", response)

    # questions = [
    #     "Which configuration has the highest `perf_high` value?",
    #     "What is the range of `inittime_high` across all configurations?",
    #     "How does `latency_high` vary between configurations?",
    #     "Which configuration has the lowest `overhead_low` value?",
    #     "What is the average count of `perf-drop` events per configuration?",
    #     "How many unique event types are there in df2?",
    #     "Which configuration has the highest number of `perf-gain` events?",
    #     "What is the maximum and minimum value for `perf-normal` events?",
    #     "How do `inittimescalable_high` and `inittimescalable_low` compare across configurations?",
    #     "Are there any correlations between high and low performance metrics?"
    # ]
    # for question in questions:
    #     response = agent.invoke({"input": question})
    #     print("Response:", response)



