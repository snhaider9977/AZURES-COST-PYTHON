import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
import os
from datetime import datetime, timedelta
from jinja2 import Template



subscription_id = 'xxxxxxxxxxxxxxxx'
tenant_id ='xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
client_id = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
client_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# Authenticate with Azure AD and get access token
auth_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/token'
auth_data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
    'resource': 'https://management.azure.com/'
}
auth_response = requests.post(auth_url, data=auth_data)
access_token = auth_response.json()['access_token']


usage_url = f'https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.CostManagement/query?api-version=2019-11-01'
usage_data = {
    'type': 'Usage',
    'timeframe': 'Custom',
    'timePeriod': {
        'from': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT00:00:00Z'),
        'to': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT23:59:59Z')
    },
    'dataset': {
        'granularity': 'Daily',
        'aggregation': {
            'totalCost': {
                'name': 'Cost',
                'function': 'Sum'
            }
        },
        'grouping': [
            {
                'type': 'Dimension',
                'name': 'ServiceName'
            }
        ]
    }
}

today = datetime.now() - timedelta(days=1)
start_of_month = datetime(today.year, today.month, 1).strftime('%Y-%m-%dT00:00:00Z')
end_of_month = (datetime(today.year, today.month+1, 1) - timedelta(days=1)).strftime('%Y-%m-%dT23:59:59Z')

usage_data_2 = {
    'type': 'Usage',
    'timeframe': 'Custom',
    'timePeriod': {
        'from': start_of_month,
        'to': end_of_month
    },
    'dataset': {
        'granularity': 'Monthly',
        'aggregation': {
            'totalCost': {
                'name': 'Cost',
                'function': 'Sum'
            }
        },
        'grouping': [
            {
                'type': 'Dimension',
                'name': 'ServiceName'
            }
        ]
    }
}

usage_response = requests.post(usage_url, headers={'Authorization': f'Bearer {access_token}'}, json=usage_data)
usage_response_2 = requests.post(usage_url, headers={'Authorization': f'Bearer {access_token}'}, json=usage_data_2)

# Extract the cost data and print the top 5 services by cost
cost_data = usage_response.json()['properties']['rows']

#for Monthly
cost_data_M = usage_response_2.json()['properties']['rows']
total_cost_M = sum([row[0] for row in cost_data_M])
monthly_budget = 500000  # 5 lakh INR
percent_consumed = (total_cost_M / monthly_budget) * 100

# convert the list of lists to a list of dictionaries
cost_data = [
    {
        'cost': row[0],
        'date': row[1],
        'service': row[2],
        'currency': row[3]
    }
    for row in cost_data
]

# calculate the total cost and the date of the total cost
total_cost = 0
total_cost_date = None
for row in cost_data:
    if total_cost_date is None or row['date'] > total_cost_date:
        total_cost_date = row['date']
        date_obj = datetime.strptime(str(total_cost_date), "%Y%m%d")
        total_cost_date_1 = date_obj.strftime("%Y-%m-%d")
    total_cost += row['cost']

# sort the list of dictionaries by cost in descending order
cost_data_sorted = sorted(cost_data, key=lambda k: k['cost'], reverse=True)

# print the total cost and its date
print(f'Total cost on {total_cost_date_1}: {total_cost} {cost_data[0]["currency"]}')
print(f'Total cost for current month: {total_cost_M} INR')
print(f'Percentage of monthly budget consumed so far: {percent_consumed}%')

# print the top 5 services by cost
print('Top 5 services by cost:')
for i, row in enumerate(cost_data_sorted[:6]):
    print(f"{i+1}. {row['service']} - {row['cost']} {row['currency']}")

list_items = [f"<li> {row['service']} - {row['cost']} {row['currency']}</li>" for row in cost_data_sorted]

# Create the email message
msg = MIMEMultipart()
msg['From'] = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxx'
msg['To'] = 'xxxxxxxxxxxxxxxxxxxxxxxxxxx'
msg['Subject'] = 'Daily Azure cost Update'

# Create the body of the email
# Create the body of the email


template = Template('''
<html>
    <body>
        <h2 style="color:blue;"> Azure costs for yesterday: </h2>
        <p> Total cost for current month: {{ total_cost_M }} INR</p>
        <p  style="color:red;"> Percentage of monthly budget consumed so far: {{ percent_consumed }} %</p>
        <p> Total cost on {{ total_cost_date_1 }}: {{ total_cost }} {{ cost_data[0]["currency"] }}</p>

        <h3 style="color:blue;"> Top 5 services by cost: </h3>
        <ol>
        {% for row in cost_data_sorted[:5] %}
            <li>{{ row["service"] }} - {{ row["cost"] }} {{ row["currency"] }}</li>
        {% endfor %}
        </ol>
    </body>
</html>
''')

body = template.render(total_cost_date_1=total_cost_date_1, total_cost=total_cost, cost_data=cost_data, cost_data_sorted=cost_data_sorted, total_cost_M = total_cost_M, percent_consumed = percent_consumed )



msg.attach(MIMEText(body, 'html'))


# Send the email
with smtplib.SMTP('smtp.office365.com', 587) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login('xxxxxxxxxxxxxxxxxxx', 'xxxxxxxxxxxxxxxxxx')
    smtp.send_message(msg)
    print('Email sent successfully.')
