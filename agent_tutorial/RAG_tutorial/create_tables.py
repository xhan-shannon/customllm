import mysql.connector
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

cursor = mysql_conn.cursor()

# Create NCCLTaskRun table
create_task_run_table = """
CREATE TABLE IF NOT EXISTS NCCLTaskRun (
    id INT AUTO_INCREMENT PRIMARY KEY,
    taskId INT,
    task_type VARCHAR(255),
    task_cycle VARCHAR(255),
    task_config VARCHAR(255),
    conn_interface VARCHAR(255),
    nccl_ver VARCHAR(255),
    node_amount INT,
    node_name VARCHAR(255),
    machine_arch VARCHAR(255),
    linux_kernel_ver VARCHAR(255),
    cuda_toolkit_ver VARCHAR(255),
    host_os VARCHAR(255),
    gpu_model VARCHAR(255),
    gpu_num INT,
    host_cpu VARCHAR(255),
    created_at DATETIME,
    created_by VARCHAR(255)
);
"""

# Create ItemData table
create_item_data_table = """
CREATE TABLE IF NOT EXISTS ItemData (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nccl_task_run_id INT,
    suiteName VARCHAR(255),
    osType VARCHAR(255),
    suiteOrder INT,
    caseId VARCHAR(255),
    dataType VARCHAR(255),
    messageSize VARCHAR(255),
    caseName VARCHAR(255),
    caseIndex INT,
    avg DECIMAL(20, 6),
    stdev DECIMAL(20, 6) NULL,
    median DECIMAL(20, 6) NULL,
    zscore DECIMAL(20, 6) NULL,
    bugs TEXT,
    FOREIGN KEY (nccl_task_run_id) REFERENCES NCCLTaskRun(id) ON DELETE CASCADE
);
"""

# Execute table creation commands
try:
    logging.info("Creating NCCLTaskRun table...")
    cursor.execute(create_task_run_table)
    logging.info("NCCLTaskRun table created successfully.")

    logging.info("Creating ItemData table...")
    cursor.execute(create_item_data_table)
    logging.info("ItemData table created successfully.")
except mysql.connector.Error as err:
    logging.error(f"Error: {err}")
    mysql_conn.rollback()
    exit(1)

# Commit changes and close connections
mysql_conn.commit()
cursor.close()
mysql_conn.close()

logging.info("Tables created successfully and connection closed.")