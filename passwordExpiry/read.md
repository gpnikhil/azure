# Password Expiry Notification Script

This Python script is designed to notify users via email when their Microsoft 365 passwords are about to expire or have already expired. It integrates with Microsoft Graph API to retrieve user password information and uses SendGrid to send email notifications.

## Features

- Retrieves user password information using Microsoft Graph API.
- Notifies users via email when their passwords are approaching the 90-day expiration.
- Sends reminders at 15, 7, 3, and 1 days before password expiration.
- Alerts users if their passwords have expired beyond 90 days.

## Prerequisites

Before running the script, ensure you have the following:

- **Python 3.6+** installed on your machine.
- A **Microsoft Azure tenant ID**, client ID, and client secret.
- A **SendGrid API key** for sending email notifications.
- **Environment variables** set for secure storage of sensitive information.
- **Microsoft Graph API permissions**: 
  - `User.Read.All`
  - `Directory.Read.All`

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/password-expiry-notification.git
    cd password-expiry-notification
    ```

2. Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Set up the following environment variables before running the script. You can do this by creating a `.env` file in the project root or exporting them in your shell:

```env
TENANT_ID=your-tenant-id
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret
SENDGRID_API_KEY=your-sendgrid-api-key
