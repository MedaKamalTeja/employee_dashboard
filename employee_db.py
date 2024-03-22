import csv
import io
from flask import Flask, render_template, request, redirect, url_for, make_response
import calendar

app = Flask(__name__)

# Read CSV files
def read_csv(filename):
    data = []
    with open(filename, 'r', newline='', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row)
    return data

# Read non-business days CSV file
def read_non_business_days(filename):
    data = []
    with open(filename, 'r', newline='', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row)
    return data

master_sheet = read_csv("Master.csv")
attendance_data = read_csv("attendence_data.csv")
non_business_days_data = read_non_business_days("non-businessdays.csv")

# Function to check if a date is a non-business day
def is_non_business_day(date):
    return any(entry['Date'] == date for entry in non_business_days_data)
@app.route('/non_business_days')
def non_business_days():
    # Get the selected month from the request parameters
    year = int(request.args.get('year', 2024))  # Default year is 2024
    month = int(request.args.get('month', 1))    # Default month is January (1)

    # Create a calendar object
    cal = calendar.Calendar()

    # Get the non-business days for the selected month
    non_business_days = []
    for day in cal.itermonthdays(year, month):
        if day == 0:  # Skip days that are not part of the current month
            continue
        weekday = calendar.day_name[calendar.weekday(year, month, day)]
        if weekday in ['Saturday', 'Sunday']:
            non_business_days.append(f"{day}-{weekday[:3]}")

    # Render the template with the non-business days data
    return render_template('non_business_days.html', non_business_days=non_business_days)

@app.route('/')
def index():
    return render_template('index_db.html')

@app.route('/search', methods=['POST'])
def search_employee():
    option = request.form.get('option', '').strip().lower()
    value = request.form.get('value', '').strip()

    if option and value:
        # Initialize an empty list to store matching employees
        matching_employees = []
        # Initialize manager_name to an empty string
        manager_name = ""

        # Find employees based on the selected option and value
        if option == 'psi_id':
            # Check if the value is a manager's PSI ID
            matching_manager = [manager for manager in master_sheet if value == manager['Employee Code']]
            if matching_manager:
                manager_name = matching_manager[0]['Employee Name']
                # Find reportees of the manager
                matching_employees = [employee for employee in master_sheet if value == employee['Reporting Manager']]
        elif option == 'location':
            matching_employees = [employee for employee in master_sheet if value.lower() == employee['Location'].lower()]
        elif option == 'bu':
            matching_employees = [employee for employee in master_sheet if value.lower() == employee['BU'].lower()]
        elif option == 'project':
            matching_employees = [employee for employee in master_sheet if value.lower() == employee['Project'].lower()]
        elif option == 'manager_name':
            # Find manager by name
            matching_manager = [manager for manager in master_sheet if value.lower() in manager['Employee Name'].lower()]
            if matching_manager:
                manager_code = matching_manager[0]['Employee Code']
                # Find reportees of the manager
                matching_employees = [employee for employee in master_sheet if manager_code == employee['Reporting Manager']]
                manager_name = value  # Set manager_name based on the searched manager's name
        elif option == 'employee_name':
            matching_employees = [employee for employee in master_sheet if value.lower() in employee['Employee Name'].lower()]

        if matching_employees:
            # Initialize an empty list to store attendance details of employees
            attendance_details = []
            # Iterate through each matching employee and fetch their attendance details
            for employee in matching_employees:
                employee_code = employee['Employee Code']
                # Find attendance details for the current employee
                employee_attendance = [attendance for attendance in attendance_data if attendance['Employee Code'] == employee_code]
                
                # Mark non-business days in attendance details
                for attendance in employee_attendance:
                    date = attendance.get('Date')
                    if date and is_non_business_day(date):
                        attendance['Non-Business Day'] = True
                    else:
                        attendance['Non-Business Day'] = False
                
                # Append attendance details to the list
                attendance_details.append({'employee': employee, 'attendance': employee_attendance})

            # Fetch non-business day information
            non_business_days = non_business_days_data

            # Determine the heading based on the search option
            if option == 'manager_name':
                heading = f"Search Results for:{manager_name}"
            elif option == 'location':
                heading = f"Search Results for:{value}"
            elif option == 'bu':
                heading = f"Search Results for:{value}"
            elif option == 'project':
                heading = f"Search Results for:{value}"
            elif option == 'psi_id':
                heading = f"Search Results for Manager {manager_name}" if manager_name else "Search Results"
            elif option == 'employee_name':
                heading = f"Search Results for employee-{value}"

            return render_template('results.html', employees=attendance_details, non_business_days=non_business_days, heading=heading)
        else:
            return render_template('error.html', message="No employees found with the specified filters.")
    else:
        return redirect(url_for('index'))


def generate_csv(data):
    csv_output = io.StringIO()
    csv_writer = csv.DictWriter(csv_output, fieldnames=data[0].keys())
    csv_writer.writeheader()
    csv_writer.writerows(data)
    return csv_output.getvalue()

@app.route('/download_csv', methods=['POST'])
def download_csv():
    csv_data = request.form.get('csv_data')
    if csv_data:
        # Convert string CSV data back to bytes
        csv_bytes = csv_data.encode('utf-8')
        
        # Create a response with CSV data
        response = make_response(csv_bytes)
        
        # Set headers for file download
        response.headers["Content-Disposition"] = "attachment; filename=attendance_data.csv"
        response.headers["Content-type"] = "text/csv"
        
        return response
    else:
        return render_template('error.html', message="No data to download.")
if __name__ == '__main__':
    app.run(debug=True)
