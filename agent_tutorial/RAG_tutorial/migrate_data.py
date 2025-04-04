import logging
from elasticsearch import Elasticsearch
from elasticsearch import RequestsHttpConnection
from elasticsearch_dsl import Search, Q
import mysql.connector
import time  # Add explicit time import

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Connect to Elasticsearch
es = Elasticsearch(
    "10.23.137.162",
    port=9200,
    connection_class=RequestsHttpConnection,
    http_auth=('elastic', 'xv=8rmkQuB=MYjcrk*Ik'),
    use_ssl=True,
    verify_certs=False,
    timeout=30,
    max_retries=10,
    retry_on_timeout=True
)

# Connect to MySQL
try:
    mysql_conn = mysql.connector.connect(
        host="10.117.4.189",
        user="swqa",
        password="labuser",
        database="datapad"
    )
    cursor = mysql_conn.cursor()
    logging.info("Connected to MySQL database.")
except mysql.connector.Error as err:
    logging.error(f"Error connecting to MySQL: {err}")
    exit(1)

# Define the Elasticsearch index and SQL insert queries
index_name = "project-nccl"  # Replace with your Elasticsearch index name
insert_task_query = """
INSERT INTO NCCLTaskRun (taskId, task_type, task_cycle, task_config, conn_interface,
                          nccl_ver, node_amount, node_name, machine_arch,
                          linux_kernel_ver, cuda_toolkit_ver, host_os,
                          gpu_model, gpu_num, host_cpu, created_at, created_by)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

insert_item_query = """
INSERT INTO ItemData (nccl_task_run_id, suiteName, osType, suiteOrder,
                      caseId, dataType, messageSize,
                      caseName, caseIndex, avg,
                      stdev, median, zscore,
                      bugs)
VALUES (%s, %s, %s, %s,
        %s, %s, %s,
        %s, %s, %s,
        %s, %s, %s,
        %s)
"""

# Fetch data from Elasticsearch using scroll API directly
try:
    # Initialize the scroll scan for retrieving all documents
    total_processed = 0

    # Use scan helper to iterate through documents
    q = Q('match_all')

    s = Search(
        using=es,
        index="project-nccl"
    ).query(q)

    search_results_data = s.scan()

    for hit in search_results_data:
        source = hit.to_dict()
        total_processed += 1

        try:
            # Validate and convert gpu_num
            gpu_num = source.get('gpu_num', 0)
            try:
                gpu_num = int(gpu_num)
            except (ValueError, TypeError):
                logging.warning(f"Invalid gpu_num '{gpu_num}' for taskId {source.get('taskId', 'unknown')}, defaulting to 0")
                gpu_num = 0

            # Add logging for data quality issues
            original_gpu_num = source.get('gpu_num')
            if original_gpu_num == '' or original_gpu_num is None:
                logging.warning(f"Empty gpu_num value for taskId {source['taskId']}, defaulting to 0")
            elif str(original_gpu_num) != str(gpu_num):
                logging.warning(f"Invalid gpu_num value '{original_gpu_num}' for taskId {source['taskId']}, converted to {gpu_num}")

            task_data_tuple = (
                source['taskId'],
                source['task_type'],
                source['task_cycle'],
                source['task_config'],
                source['conn_interface'],
                source['nccl_ver'],
                source['node_amount'],
                source['node_name'],
                source['machine_arch'],
                source['linux_kernel_ver'],
                source['cuda_toolkit_ver'],
                source['host_os'],
                source['gpu_model'],
                gpu_num,  # Use the validated gpu_num value
                source['host_cpu'],
                source['created_at'],
                source['created_by']
            )

            cursor.execute(insert_task_query, task_data_tuple)
            nccl_task_run_id = cursor.lastrowid

            if total_processed % 100 == 0:  # Log every 100 documents
                logging.info(f"Processed document {total_processed}: taskId {source['taskId']}")

            # Insert itemData
            for item in source.get('itemData', []):
                for case_item in item.get('caseItems', []):
                    try:
                        avg = float(case_item.get('avg', 0))
                    except ValueError:
                        logging.error(f"Invalid avg value '{case_item.get('avg')}' for taskId {source['taskId']}, setting to 0")
                        avg = 0

                    try:
                        stdev = float(case_item.get('stdev')) if case_item.get('stdev') else None
                    except ValueError:
                        logging.error(f"Invalid stdev value '{case_item.get('stdev')}' for taskId {source['taskId']}, setting to None")
                        stdev = None

                    try:
                        median = float(case_item.get('median')) if case_item.get('median') else None
                    except ValueError:
                        logging.error(f"Invalid median value '{case_item.get('median')}' for taskId {source['taskId']}, setting to None")
                        median = None

                    try:
                        zscore = float(case_item.get('zscore')) if case_item.get('zscore') else None
                    except ValueError:
                        logging.error(f"Invalid zscore value '{case_item.get('zscore')}' for taskId {source['taskId']}, setting to None")
                        zscore = None

                    item_data_tuple = (
                        nccl_task_run_id,
                        item['suiteName'],
                        item.get('osType', ''),
                        item.get('suiteOrder', -1),
                        case_item.get('caseId', ''),
                        case_item.get('dataType', ''),
                        case_item.get('messageSize', ''),
                        case_item.get('caseName', ''),
                        case_item.get('caseIndex', -1),
                        avg,
                        stdev,
                        median,
                        zscore,
                        case_item.get('bugs', '')
                    )

                    cursor.execute(insert_item_query + " ON DUPLICATE KEY UPDATE bugs=VALUES(bugs)", item_data_tuple)

            # Commit after each document
            mysql_conn.commit()

        except mysql.connector.Error as err:
            logging.error(f"Error inserting data into MySQL: {err}")
            mysql_conn.rollback()
            continue

        # Add a small delay every 1000 documents to prevent overwhelming the server
        if total_processed % 1000 == 0:
            time.sleep(0.1)

    logging.info(f"Total documents processed: {total_processed}")

except Exception as e:
    logging.error(f"Error fetching data from Elasticsearch: {e}")
    exit(1)

finally:
    # Close connections
    cursor.close()
    mysql_conn.close()
    logging.info("Connections closed.")