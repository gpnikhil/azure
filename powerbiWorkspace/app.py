import requests
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting
import sys

# Ensure connection string is provided
if len(sys.argv) < 2:
    print("Connection string not provided.")
    sys.exit(1)

# Connection string for Azure App Configuration
connection_string = sys.argv[1]
client = AzureAppConfigurationClient.from_connection_string(connection_string)

# Retrieve configuration values from Azure App Configuration
app_config = {
    'client_id': client.get_configuration_setting('powerbi.client.id').value,
    'client_secret': client.get_configuration_setting('powerbi.client.secret').value,
    'tenant_id': client.get_configuration_setting('powerbi.tenant.id').value,
}

# OAuth2 token endpoint
token_url = f'https://login.microsoftonline.com/{app_config["tenant_id"]}/oauth2/v2.0/token'
scope = 'https://analysis.windows.net/powerbi/api/.default'

# Request access token
token_data = {
    'grant_type': 'client_credentials',
    'client_id': app_config['client_id'],
    'client_secret': app_config['client_secret'],
    'scope': scope
}
response = requests.post(token_url, data=token_data)
access_token = response.json().get('access_token')

# Headers for API requests
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Define a static workspace name
workspace_name = 'YourWorkspaceName'

# Check if the workspace already exists
workspace_url = 'https://api.powerbi.com/v1.0/myorg/groups'
response = requests.get(workspace_url, headers=headers)
workspaces = response.json().get('value', [])
workspace_id = next((w['id'] for w in workspaces if w['name'] == workspace_name), None)

# If workspace does not exist, create it
if not workspace_id:
    workspace_data = {'name': workspace_name}
    response = requests.post(workspace_url, headers=headers, json=workspace_data)
    workspace_id = response.json().get('id')

    # Save workspace ID in Azure App Configuration for future reference
    client.set_configuration_setting(ConfigurationSetting(
        key='powerbi.workspace.id',
        value=workspace_id
    ))

    # Add a user to the new workspace as an admin
    add_user_url = f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/users'
    user_data = {
        "emailAddress": "replace_with_user_email@example.com",  # Replace with the admin email
        "groupUserAccessRight": "Admin"
    }
    requests.post(add_user_url, headers=headers, json=user_data)

    # Assign the workspace to a Power BI Embedded capacity
    assign_capacity_url = f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/AssignToCapacity'
    capacity_data = {
        'capacityId': 'replace_with_capacity_id'  # Replace with actual capacity ID
    }
    requests.post(assign_capacity_url, headers=headers, json=capacity_data)
else:
    print(f"Workspace '{workspace_name}' already exists with ID: {workspace_id}")
