from google.oauth2 import service_account
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

# Path to your downloaded credentials.json file
SERVICE_ACCOUNT_FILE = 'sharadgupta5678@marine-clarity-313813.iam.gserviceaccount.com'

# Scopes required by Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Authenticate using the service account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the Gmail service
service = build('gmail', 'v1', credentials=credentials)

# Example: Send an email using the Gmail API
def send_email(to_email, subject, body):
    message = MIMEText(body)
    message['to'] = to_email
    message['from'] = 'shardgupta65@gmail.com'  # Replace with your email
    message['subject'] = subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        send_message = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        print(f'Sent message to {to_email}')
    except Exception as error:
        print(f'An error occurred: {error}')

# Send a test email
send_email('recipient@example.com', 'Test Subject', 'This is a test email body')
