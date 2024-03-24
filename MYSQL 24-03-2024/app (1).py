# import tempfile
#
from flask import Flask, render_template, request, send_file
from flask import session, Response
import pandas as pd
#
app = Flask(__name__)
#
# # Read the employee data from the Excel files
df_master = pd.read_excel(r"C:\Users\Balaji J - 3303\PycharmProjects\Emp_data\Mastersheetsmartoffice.xlsx")
df_employee_data = pd.read_excel(r"C:\Users\Balaji J - 3303\PycharmProjects\Emp_data\Employee_data.xlsx")

app.secret_key = '12ert4'
@app.route('/')
def index():
    # Render the index.html template
    return render_template('home_page.html')


@app.route('/search', methods=['POST'])
def search():
    # Get the search term from the form
    search_term = request.form['search_term']

    # Check if the search term matches any reporting manager in the Mastersheetsmartoffice.xlsx file
    if search_term in df_master['Reporting Manager'].values:
        # Get the employee name and additional columns from Employee_data.xlsx based on the search term (assuming 'Code' is the column name)
        reporting_manager_data = df_employee_data[df_employee_data['Code'] == search_term]

        if reporting_manager_data.empty:
            return render_template('search_result.html',
                                   message=f"No data found for reporting manager with the code {search_term}.")

        manager_name = reporting_manager_data['Emp Name'].iloc[0]

        # Filter the employee data based on the reporting manager in the Mastersheetsmartoffice.xlsx file
        filtered_data = df_master[df_master['Reporting Manager'] == search_term]

        if filtered_data.empty:
            message = f"No employees found working under {search_term}"
        else:
            message = f"Employees working under {search_term}"

            # Merge additional columns from Employee_data.xlsx based on Employee Code
            merged_data = pd.merge(filtered_data, df_employee_data, left_on='Employee Code', right_on='Code',
                                   how='left')
            columns_to_exclude = ['Designation', 'Building', 'Reporting Manager', 'BU', 'Project', 'Location', 'No',
                                  'Code', 'Emp Name',
                                  '1-Fri', '2-Sat', '3-Sun', '4-Mon', '5-Tue', '6-Wed', '7-Thu', '8-Fri', '9-Sat',
                                  '10-Sun',
                                  '11-Mon', '12-Tue', '13-Wed', '14-Thu', '15-Fri', '16-Sat', '17-Sun', '18-Mon',
                                  '19-Tue', '20-Wed']

            # List of columns to retain in merged_data
            columns_to_retain = [col for col in merged_data.columns if col not in columns_to_exclude]

            # Extracting specified columns from merged_data
            merged_data = merged_data[columns_to_retain]
            # Convert merged data to a dictionary for rendering in HTML
            data = merged_data.to_dict('records')

            # Store merged_data in session
            session['merged_data'] = merged_data.to_csv(index=False)

        # Render the template with the data
        return render_template('result.html', data=data, manager_name=manager_name, message=message)

    else:
        # If the search term doesn't match any reporting manager, display an error message
        return render_template('result.html', message=f"No reporting manager found with the code {search_term}.")

@app.route('/download_csv')
def download_csv():
    # Retrieve merged_data from session
    merged_data_csv = session.get('merged_data')

    if merged_data_csv is None:
        return "No data available to download as CSV"

    # Send the CSV data as a response
    return Response(
        merged_data_csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=merged_data.csv"})
if __name__ == '__main__':
    app.run(debug=True)