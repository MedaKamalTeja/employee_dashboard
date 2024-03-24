from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Database configuration
db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="root",
    database="local instance mysql83"
)
cursor = db.cursor()

# Route to display search form
@app.route('/')
def index():
    return render_template('index_db.html')

# Route to handle search form submission and redirect to results page
@app.route('/search', methods=['POST'])
def search():
    psi_id = request.form.get('psi_id')
    if not psi_id:
        return "Please provide a PSI ID for search."
    
    try:
        # Check if the PSI ID exists in the master table
        cursor.execute("SELECT * FROM master WHERE `Employee Code` = %s", (psi_id,))
        manager_info = cursor.fetchone()
        
        # If PSI ID not found, display error message
        if manager_info is None:
            return "Manager not found."
        
        # Fetch the reporting manager's details from the master table
        cursor.execute("SELECT * FROM master WHERE `Reporting Manager` = %s", (psi_id,))
        employees_reporting_to_manager = cursor.fetchall()
        
        # Initialize a list to store employee attendance data
        employee_attendance = []
        
        # Iterate through the employees reporting to the manager and fetch their attendance data
        for employee in employees_reporting_to_manager:
            employee_psi_id = employee[0]
            cursor.execute("SELECT * FROM attendence_data WHERE `Employee Code` = %s", (employee_psi_id,))
            employee_attendance.extend(cursor.fetchall())
        
        # Pre-process date range for the template
        date_range = [f"{i}" for i in range(1, 22)]  # Example date range, you can replace it with your actual data
        
        # Redirect to the results page with manager and employee attendance data
        return render_template('results.html', manager_info=manager_info, employee_attendance=employee_attendance, date_range=date_range)
    
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
