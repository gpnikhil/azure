# Power BI Workspace Management Script

This Python script automates the creation and management of Power BI workspaces using the Power BI REST API and Azure App Configuration. It streamlines the process of workspace creation, user management, and capacity assignment.

## Table of Contents

- [Power BI Workspace Management Script](#power-bi-workspace-management-script)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Usage](#usage)
  - [Configuration](#configuration)
  - [How It Works](#how-it-works)
  - [License](#license)

## Prerequisites

Before using this script, ensure you have the following:

1. **Azure App Configuration** set up with your Power BI API credentials and tenant information.
2. **Python 3.7+** installed on your machine.
3. Required Python libraries:
   ```bash
   pip install azure-appconfiguration requests
   ```
4. A registered application in Azure AD with relevant permissions for Power BI API:
   - **Application (client) ID**
   - **Client Secret**
   - **Tenant ID**


## Usage

To run the script, you need to provide the connection string for Azure App Configuration as a command-line argument:

```bash
python app.py "Your_Azure_App_Configuration_Connection_String"
```

## Configuration

You will need to create the following keys in your Azure App Configuration:

| Key                        | Description                          |
|----------------------------|--------------------------------------|
| **`powerbi.client.id`**    | Power BI Client ID                  |
| **`powerbi.client.secret`**| Power BI Client Secret              |
| **`powerbi.tenant.id`**    | Tenant ID for authentication        |
| **`powerbi.workspace.id`** | Workspace ID (generated on creation)|

## How It Works

1. **Configuration Setup**: The script retrieves API credentials from Azure App Configuration.
2. **OAuth2 Authentication**: It obtains an OAuth2 token from Azure AD for authenticating API requests.
3. **Workspace Management**: 
   - Checks if a workspace with the specified name exists.
   - Creates a new workspace if it doesn’t exist.
   - Adds a user as an admin to the workspace.
   - Assigns the workspace to a specified Power BI Embedded capacity.
4. **Storing Workspace ID**: The workspace ID is stored in Azure App Configuration for future reference.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Feel free to modify any sections to better fit your project's specifics!