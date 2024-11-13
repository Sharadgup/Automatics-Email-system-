from flask import Flask, render_template, request, jsonify
import pdfplumber
import re
import os
from email.mime.text import MIMEText
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'  # Directory for uploaded files

# Gmail API Setup
creds = service_account.Credentials.from_service_account_file('credentials.json')
service = build('gmail', 'v1', credentials=creds)

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def extract_emails(pdf_path):
    """Extract emails from a PDF file."""
    emails = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            emails.extend(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text))
    return list(set(emails))  # Removing duplicates

def extract_template_text(template_path):
    """Extract text from an email template PDF."""
    with pdfplumber.open(template_path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages)

def send_email(recipient_email, template_text):
    """Send email using Gmail API."""
    message = MIMEText(template_text.replace("{email}", recipient_email))
    message['to'] = recipient_email
    message['from'] = "your_email@gmail.com"
    message['subject'] = "Subject of Your Email"

    raw_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    try:
        service.users().messages().send(userId="me", body=raw_message).execute()
        return f"Sent email to {recipient_email}"
    except Exception as e:
        return f"Error sending email to {recipient_email}: {e}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    pdf_file = request.files.get('pdfFile')
    template_file = request.files.get('templateFile')
    if not pdf_file or not template_file:
        return jsonify({"error": "Both PDF and Template files are required"}), 400

    # Save files to upload directory
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename)
    template_path = os.path.join(app.config['UPLOAD_FOLDER'], template_file.filename)
    pdf_file.save(pdf_path)
    template_file.save(template_path)

    # Extract emails and template text
    emails = extract_emails(pdf_path)
    template_text = extract_template_text(template_path)

    # Send emails
    status_messages = [send_email(email, template_text) for email in emails]

    return jsonify({"status": status_messages})

if __name__ == '__main__':
    app.run(debug=True)
