import msal
import requests
import os
from datetime import datetime, timedelta
import sendgrid
from sendgrid.helpers.mail import Mail

# Configuration
TENANT_ID = os.getenv('TENANT_ID')  # Replace with environment variable
CLIENT_ID = os.getenv('CLIENT_ID')  # Replace with environment variable
CLIENT_SECRET = os.getenv('CLIENT_SECRET')  # Replace with environment variable
AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
SCOPE = ["https://graph.microsoft.com/.default"]
domain = "maisteringdev.onmicrosoft.com"
GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0/users'
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')  # Replace with environment variable
FROM_EMAIL = 'tech.support@maistering.com'

# Function to parse datetime with or without microseconds
def parse_datetime(date_string):
    try:
        # Try parsing without microseconds
        return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        # Fallback for datetime strings with microseconds
        return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")

# Get access token
def get_access_token():
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=SCOPE)
    if "access_token" in result:
        return result['access_token']
    else:
        raise Exception("Could not obtain access token")

# Get password expiry information
def get_user_password_expiry(user_id, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(f'{GRAPH_API_ENDPOINT}/{user_id}/authentication/passwordMethods', headers=headers)
    if response.status_code == 200:
        data = response.json()
        for method in data['value']:
            password_last_changed = method.get("createdDateTime")
            if password_last_changed:
                return parse_datetime(password_last_changed)
    else:
        raise Exception(f"Error retrieving user data: {response.status_code} - {response.text}")

# Get all users with emails in the specified domain
def get_all_users_emails(access_token, domain_filter):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    users = []
    next_link = GRAPH_API_ENDPOINT
    while next_link:
        response = requests.get(next_link, headers=headers)
        if response.status_code == 200:
            data = response.json()
            users.extend([user['mail'] for user in data['value'] if user.get('mail') and user['mail'].endswith(domain_filter)])
            next_link = data.get('@odata.nextLink')
        else:
            raise Exception(f"Error retrieving users: {response.status_code} - {response.text}")
    return users

# Send email notification using SendGrid
def send_email_notification(email, days_left):
    sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)
    if days_left <= 0:
        subject = f"Password Change Overdue"
        content = f"Your password has not been changed in over 90 days. Please update it immediately."
    else:
        subject = f"Password change needed {days_left} day(s) left"
        content = f"Your password needs to be changed in {days_left} day(s)"
    
    message = Mail(from_email=FROM_EMAIL, to_emails=email, subject=subject, plain_text_content=content)
    response = sg.send(message)
    
    if response.status_code not in [200, 202]:
        print(f"Failed to send email to {email}: {response.status_code} - {response.body}")
    else:
        print(f"Email sent to {email}: {response.status_code}")

if __name__ == '__main__':
    try:
        token = get_access_token()
        user_emails = get_all_users_emails(token, domain)
        for email in user_emails:
            password_last_changed = get_user_password_expiry(email, token)
            if password_last_changed:
                days_old = (datetime.utcnow() - password_last_changed).days
                days_to_expiry = 90 - days_old
                
                # Notify if password is approaching expiry
                if 0 <= days_to_expiry <= 15 and days_to_expiry in [15, 7, 3, 1]:
                    print(f"Password for {email} will expire in {days_to_expiry} day(s).")
                    send_email_notification(email, days_to_expiry)
                # Notify if password is already expired for more than 90 days
                elif days_old > 90:
                    print(f"Password for {email} is older than 90 days.")
                    send_email_notification(email, 0)
    except Exception as e:
        print(f"An error occurred: {e}")
