import csv
import mysql.connector

# MySQL database connection
db_connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="root",
    database="local instance mysql83"
)

# Create cursor object
cursor = db_connection.cursor()

# Create tables
create_table_queries = [
    """
    CREATE TABLE IF NOT EXISTS employees (
        employee_id INT PRIMARY KEY,
        reporting_manager_id INT,
        location_id INT,
        name VARCHAR(255),
        title VARCHAR(255),
        location VARCHAR(255),
        project VARCHAR(255),
        BU VARCHAR(255),
        email VARCHAR(255)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS attendance (
        employee_id INT,
        date DATE,
        time_in TIME,
        time_out TIME,
        total_duration INT,
        attendance_status VARCHAR(255),
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS non_business_days (
        location_id INT,
        remarks VARCHAR(255),
        FOREIGN KEY (location_id) REFERENCES employees(location_id)
    )
    """
]

# Execute create table queries
for query in create_table_queries:
    cursor.execute(query)

# Insert data from CSV files
def insert_data_from_csv(file_path, table_name):
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            cursor.execute(f"INSERT INTO {table_name} VALUES ({', '.join(['%s']*len(row))})", row)

# Insert data into employees table
insert_data_from_csv('Master.csv', 'employees')

# Insert data into attendance table
insert_data_from_csv('attendance_data.csv', 'attendance')

# Insert data into non_business_days table
insert_data_from_csv('non-businessdays.csv', 'non_business_days')

# Commit changes and close connection
db_connection.commit()
cursor.close()
db_connection.close()
