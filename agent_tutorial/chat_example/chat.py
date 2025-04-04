import requests
import pandas as pd
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from openai import OpenAI


if __name__ == "__main__":
    # Initialize ChatOpenAI client with local deepseek model
    # Using localhost:7869 as the base URL for the API
    # No API key needed for local deployment
    # Using deepseek-r1 70B model with temperature=0 for consistent outputs
    client = OpenAI(
        base_url="http://localhost:7869/v1",
        api_key="no-need",

    )

    # Assuming the correct method is `create_completion` instead of `chat.completions.create`
    response = client.chat.completions.create(
      model="deepseek-r1:70b",
      response_format={"type": "json_object"},
      messages=[
        {"role": "system", "content": "你是一个专业研究生论文写作助手，帮助学生和老师在体育相关专业回答问题."},
        {"role": "user", "content": "云南民族大学体育学院的体育教育专业有哪些研究方向？"}
      ]
    )
    print(response)
