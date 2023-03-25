# Azure Cost Management Export Automation
This Python script automates the export of Azure cost data to a storage account. It also sends a message to Microsoft Teams to notify the team of the export status.

## Dependencies
This script requires the following Python packages to be installed:

- 'azure.appconfiguration': used to authenticate with Azure using a service principal
- 'azure.identity': used to obtain an access token from Azure AD
- 'requests': used to make HTTP requests to the Azure Management API and to send the Teams message
- 'pandas': used to read the Excel file containing the export and trigger information
- 'json': used to construct the Teams message payload
- 'datetime': used to calculate the start and end times for the export
- 'logging': used to log any exceptions that occur during the export process
## Usage
1. Install the required dependencies
2. Modify the global configuration variables at the top of the script to fit your environment
3. Create an Excel file with two sheets named "Export" and "Trigger" with the following columns:
- Export:
    - Tenant Name
    - Subscription Name
    - Subscription Id
    - Storage Subscription Id
    - Export Name
    - Storage RG
    - Storage Name
    - Storage Container Name
    - Directory Name
- Trigger:
    - SL
    - Subscription Id
    - Days
4. Fill in the information in the Excel file with your subscription and storage account information
5. Schedule the script to run on a regular basis using your preferred method
## Functionality
### Teams Message Post
This function constructs and sends a message to Microsoft Teams to notify the team of the export status. The 'webhookurl' parameter should be the webhook URL for the Teams channel. The 'teamsmessage' parameter is the message to send to the channel, and the 'teamscolor' parameter is the color to use for the message.

### Cost Export Update
This section of the script reads the "Export" sheet in the Excel file and updates the cost management export for each subscription. It first calculates the start and end times for the export based on the current time and the number of days specified in the Excel file. It then loops through each row in the "Export" sheet and updates the cost management export for the corresponding subscription.

### Cost Export Trigger
This section of the script reads the "Trigger" sheet in the Excel file and triggers a cost management export for each subscription that meets the trigger conditions. The trigger conditions are specified in the "Trigger" sheet and consist of the number of days since the last export and a threshold percentage for the cost change.
