import tkinter as tk
from tkinter import filedialog, messagebox
import pdfplumber
import re
from email.mime.text import MIMEText
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build

class EmailAutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Automation Tool")
        self.pdf_path = ""
        self.template_path = ""

        # Buttons to upload PDF and Template
        self.select_pdf_btn = tk.Button(root, text="Select PDF with Emails", command=self.load_pdf)
        self.select_pdf_btn.pack(pady=10)

        self.select_template_btn = tk.Button(root, text="Select Email Template PDF", command=self.load_template)
        self.select_template_btn.pack(pady=10)

        # Button to send emails
        self.send_email_btn = tk.Button(root, text="Send Emails", command=self.send_emails)
        self.send_email_btn.pack(pady=20)

        # Status Message
        self.status_label = tk.Label(root, text="")
        self.status_label.pack()

    def load_pdf(self):
        self.pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if self.pdf_path:
            self.status_label.config(text=f"Loaded PDF: {self.pdf_path}")

    def load_template(self):
        self.template_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if self.template_path:
            self.status_label.config(text=f"Loaded Template: {self.template_path}")

    def extract_emails(self, pdf_path):
        emails = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                emails.extend(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text))
        return list(set(emails))  # Removing duplicates if any

    def extract_template_text(self, template_path):
        with pdfplumber.open(template_path) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages)

    def send_emails(self):
        if not self.pdf_path or not self.template_path:
            messagebox.showerror("Error", "Please upload both PDF and Template files")
            return

        # Extract emails and template
        emails = self.extract_emails(self.pdf_path)
        template_text = self.extract_template_text(self.template_path)

        # Initialize Gmail API
        creds = service_account.Credentials.from_service_account_file('path/to/credentials.json')
        service = build('gmail', 'v1', credentials=creds)

        for email in emails:
            # Prepare the message
            personalized_text = template_text.replace("{email}", email)
            message = MIMEText(personalized_text)
            message['to'] = email
            message['from'] = "your_email@gmail.com"
            message['subject'] = "Subject of Your Email"

            # Send the email
            raw_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
            try:
                service.users().messages().send(userId="me", body=raw_message).execute()
                self.status_label.config(text=f"Sent email to {email}")
            except Exception as e:
                self.status_label.config(text=f"Error sending email to {email}: {e}")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = EmailAutomationApp(root)
    root.mainloop()
