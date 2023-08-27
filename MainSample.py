from flask import Flask, render_template, request
import pandas as pd

df=pd.read_excel(r'D:/Excel File/Masibus.xlsx',sheet_name="Sheet1")

# Select columns that contain "alm"
cols = [col for col in df.columns if 'alm' in col.lower()]

cols.extend(["crd6a_device_id","crd6a_datetime"])

df_selected=df[cols].copy()

df_selected["Date"] = df_selected["crd6a_datetime"].apply(lambda x: x.split(" ")[0] if type(x) == str else x)
df_selected["Time"] = df_selected["crd6a_datetime"].apply(lambda x: x.split(" ")[1] if type(x) == str else x)

df_selected.sort_values(["Date", "Time"], inplace=True)

# Drop the original datetime column
df_selected.drop("crd6a_datetime", axis=1, inplace=True)

# Get the unique values from the "Device ID" column
device_ids = df_selected['crd6a_device_id'].unique()

# Create a Flask application
app = Flask(__name__)

# Define a route for the homepage
@app.route('/')
def home():
    return render_template('index.html', device_ids=device_ids)

@app.route('/submit', methods=['POST'])
def submit():
    # Get the selected device ID from the form
    device_id = request.form['device_id'] 

    # Filter the dataframe by the selected device ID
    df_filtered = df_selected[df_selected['crd6a_device_id'] == int(device_id)]
    df_filtered = df_filtered.drop('crd6a_device_id', axis=1)

    # Initialize dictionaries
    main_dict = {'Alarm Name': [], 'OnDate': [], 'OnTime': [], 'OffDate': [], 'OffTime': []}
    prev_dict = {'Alarm Name': [], 'OnDate': [], 'OnTime': [], 'OffDate': [], 'OffTime': []}

    for index, row in df_filtered.iterrows():
        # Create a new dictionary for the current row
        new_dict = {'Alarm Name': [], 'OnDate': [], 'OnTime': [], 'OffDate': [], 'OffTime': []}

        # Iterate through the alarms and check if they are on
        for column in df_filtered.columns:
            if row[column] == 1:
                new_dict['Alarm Name'].append(column)
                new_dict['OnDate'].append(row['Date'])
                new_dict['OnTime'].append(row['Time'])

        # Check if any alarms have turned off since the previous row
        for i in range(len(prev_dict['Alarm Name'])):
            if prev_dict['Alarm Name'][i] not in new_dict['Alarm Name']:
                main_dict['Alarm Name'].append(prev_dict['Alarm Name'][i])
                main_dict['OnDate'].append(prev_dict['OnDate'][i])
                main_dict['OnTime'].append(prev_dict['OnTime'][i])
                main_dict['OffDate'].append(row['Date'])
                main_dict['OffTime'].append(row['Time'])

        # Check if any new alarms have turned on
        for i in range(len(new_dict['Alarm Name'])):
            if new_dict['Alarm Name'][i] not in prev_dict['Alarm Name']:
                main_dict['Alarm Name'].append(new_dict['Alarm Name'][i])
                main_dict['OnDate'].append(new_dict['OnDate'][i])
                main_dict['OnTime'].append(new_dict['OnTime'][i])
                main_dict['OffDate'].append('')
                main_dict['OffTime'].append('')

        # Update the prev_dict
        prev_dict = new_dict.copy()

    # Convert main_dict to a list and return it to the template
    result_list = []
    for i in range(len(main_dict['Alarm Name'])):
        result_list.append({'Alarm Name': main_dict['Alarm Name'][i], 'OnDate': main_dict['OnDate'][i], 'OnTime': main_dict['OnTime'][i], 'OffDate': main_dict['OffDate'][i], 'OffTime': main_dict['OffTime'][i]})

    
    return render_template('results.html', data=result_list)
if __name__ == '__main__':
    app.run(debug=True)

