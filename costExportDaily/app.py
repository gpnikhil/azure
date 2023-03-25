from azure.appconfiguration import AzureAppConfigurationClient
from azure.identity import ClientSecretCredential
import requests
import pandas as pd
from json import loads
import json
import datetime
import logging

### Global Configurations

# Download file from Storage Account
costmgmt_file = pd.ExcelFile('https://yourblob.blob.core.windows.net/cost/azurecost.xlsx')

#### Teams Message Post
def teamsPost(webhookurl, teamsmessage, teamscolor):

    message = """{"type":"message","attachments":[{"contentType":"application/vnd.microsoft.card.adaptive","contentUrl":null,"content":{"$schema":"https://adaptivecards.io/schemas/adaptive-card.json","type":"AdaptiveCard","version":"1.4","body":[{"type":"TextBlock","size":"Large","weight":"Bolder","text":"Cost Management","spacing":"Large","horizontalAlignment":"Center","height":"stretch","style":"default","fontType":"Default","color":"Accent","isSubtle":false},{"type":"TextBlock","text":"","wrap":true,"spacing":"Padding","horizontalAlignment":"Left","height":"stretch","style":"columnHeader","fontType":"Monospace","size":"Medium","weight":"Bolder","color":""}]}}]}"""

    payloadData = dict(loads(message))

    payloadData['attachments'][0]['content']['body'][1]['text'] += teamsmessage
    payloadData["attachments"][0]['content']['body'][1]['color'] += teamscolor
    response = requests.post(
        webhookurl, data=json.dumps(payloadData),
        headers={'Content-Type': 'application/json'}
    )

    # This will log a error if the response is not 200
    if response.status_code != 200:
        raise ValueError(
            'Request to Teams returned an error %s, the response is:\n%s'
            % (requests.status_code, response.text)
        )

### Cost Export Update

# Present time calculate
now =           datetime.datetime.now()
two_days_ago =  now - datetime.timedelta(days=2)
start_time =    datetime.datetime(two_days_ago.year, two_days_ago.month, two_days_ago.day, 0, 0, 0)
end_time =      datetime.datetime(two_days_ago.year, two_days_ago.month, two_days_ago.day, 23, 59, 59)

# Excel Data read Export Sheet
export_sheet = pd.read_excel(costmgmt_file, sheet_name="Export")

# Porgram logic for Cost Export Update
for i in range(len(export_sheet)):

    if export_sheet['Tenant Name'][i] == 'Tenant Name':

        # Authenticate with Azure using a service principal for PayG
        client_id =     "clientID"
        client_secret = "clientSecret"
        tenant_id =     "tenantID"     

    # Update cost management export
    subscription_name =   export_sheet['Subscription Name'][i]
    subscription_id =     export_sheet['Subscription Id'][i]
    storage_account_sid = export_sheet['Storage Subscription Id'][i]
    export_name =         export_sheet['Export Name'][i]
    resource_group =      export_sheet['Storage RG'][i]
    storage_account =     export_sheet['Storage Name'][i]
    storage_container =   export_sheet['Storage Container Name'][i]
    storage_directory =   export_sheet['Directory Name'][i]
    start_time_iso =      start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_time_iso =        end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    try:
        endpoint = "https://management.azure.com"

        # Build the API endpoint URL
        url = f"{endpoint}/subscriptions/{subscription_id}/providers/Microsoft.CostManagement/exports/{export_name}?api-version=2021-10-01"
        
        # Authenticate with AAD and obtain an access token
        credential = ClientSecretCredential(
            tenant_id.value, client_id.value, client_secret.value)
        access_token = credential.get_token(
            "https://management.azure.com/.default").token

        # Set the authorization header
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        # Construct the request body
        body = {
            "properties": {
                "format": "Csv",
                "deliveryInfo": {
                    "destination": {
                        "ResourceId": f'/subscriptions/{storage_account_sid}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{storage_account}',
                        "container": storage_container,
                        "rootFolderPath": storage_directory
                    },
                },
                "definition": {
                    "timeframe": "Custom",
                    "timePeriod": {
                        "from": start_time_iso,
                        "to": end_time_iso
                    }
                }
            }
        }

        # Make the API call
        response = requests.put(url, headers=headers, json=body)

        # Check the response status code
        if response.status_code == 200:
            print(f'Cost Management export updated successfully for {subscription_name}')
        else:
            print(f'Error updating Cost Management export: {response.content}')
    except Exception as e:
        logging.exception(e)


### Cost Export Trigger

# Authenticate with Azure using a service principal
client_id =       "clientID"
client_secret =   "clientSecret"
tenant_id =       "tenantID"
costmgmtwebhook = "Teams Webhook URL"

# Excel Data read Trigger Sheet
triggersheet = pd.read_excel(costmgmt_file, sheet_name="Trigger")

# Porgram logic for Cost Export Trigger
for i in range(len(triggersheet["SL"])):


    subscription_id = triggersheet["Subscription Id"][i]
    export_name = triggersheet["Export Name"][i]

    # Replace with the Azure resource manager endpoint
    endpoint = "https://management.azure.com"

    # Build the API endpoint URL
    url = f"{endpoint}/subscriptions/{subscription_id}/providers/Microsoft.CostManagement/exports/{export_name}/run?api-version=2021-10-01"

    # Authenticate with AAD and obtain an access token
    credential = ClientSecretCredential(
        tenant_id.value, client_id.value, client_secret.value)
    
    access_token = credential.get_token(
        "https://management.azure.com/.default").token

    # Set the authorization header
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Send the API request
    response = requests.post(url, headers=headers)

    # Check the response status code
    if response.status_code != 200:
        teamsmessage = 'Date : {0} Error in Cost Export Triggered For {1}'.format(start_time_iso, triggersheet['Subscription Name'][i])
        teamscolor = 'Attention'
        teamsPost(costmgmtwebhook.value, teamsmessage, teamscolor)
        raise ValueError(
            'Request to Teams returned an error %s, the response is:\n%s'
            % (requests.status_code, response.text)
        )
    else:
        teamsmessage = 'Date : {0} Daily Cost Export Triggered For {1}'.format(start_time_iso, triggersheet['Subscription Name'][i])
        teamscolor = 'Good'
        teamsPost(costmgmtwebhook.value, teamsmessage, teamscolor)
