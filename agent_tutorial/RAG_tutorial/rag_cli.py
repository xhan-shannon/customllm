import mysql.connector
import openai
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def connect_to_db():
    # Connect to MySQL
    try:
        logging.info("Connecting to MySQL database...")
        mysql_conn = mysql.connector.connect(
            host="10.117.4.189",
            user="swqa",  # Replace with your username
            password="labuser",  # Replace with your password
            database="datapad"  # Replace with your database name
        )
        logging.info("Connected to MySQL database.")
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
        exit(1)

    return mysql_conn


def query_mysql(query):
    connection = connect_to_db()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(query)
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results


def generate_response(prompt):
    openai.api_key = 'your_openai_api_key'

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or any other model you prefer
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response['choices'][0]['message']['content']


def extract_task_id(user_query):
    """
    Extracts the task ID from the user query.

    Args:
        user_query (str): The query string input by the user.

    Returns:
        int: The extracted task ID, or None if not found.
    """
    # Use regular expression to find a number in the user query
    match = re.search(r'\b(\d+)\b', user_query)
    if match:
        return int(match.group(1))  # Return as an integer
    else:
        return None  # Return None if no task ID is found


def rag_process(user_query):
    # Step 1: Generate SQL query based on user input (this can be enhanced using LLM)
    if "all tasks" in user_query.lower():
        sql_query = """
        SELECT
            n.taskId,
            n.task_type,
            n.task_cycle,
            i.suiteName,
            i.caseId,
            i.caseName,
            i.avg
        FROM
            NCCLTaskRun n
        LEFT JOIN
            ItemData i ON n.taskId = i.taskId;
        """
    elif "specific task" in user_query.lower():
        task_id = extract_task_id(user_query)  # Implement this function to extract task ID from user query.
        sql_query = f"""
        SELECT
            n.*,
            i.*
        FROM
            NCCLTaskRun n
        LEFT JOIN
            ItemData i ON n.taskId = i.taskId
        WHERE
            n.taskId = {task_id};
        """
    else:
        return "Sorry, I could not understand your query."

    # Step 2: Retrieve data from MySQL
    results = query_mysql(sql_query)

    # Step 3: Prepare context for the LLM if results are found
    context = "\n".join([str(result) for result in results])

    # Step 4: Generate response using the context if there are results.
    if context:
        prompt = f"Based on the following data:\n{context}\n\nAnswer the question: {user_query}"
        answer = generate_response(prompt)
        return answer
    else:
        return "No relevant data found."


if __name__ == "__main__":
    while True:
        user_input = input("Ask a question about your data (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break

        response = rag_process(user_input)
        print("Response:", response)