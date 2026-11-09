import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import base64
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate_gmail():
    creds = None
    
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def get_email_body(payload):
    """Recursively parses the Gmail payload to extract plain text body."""
    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    body += base64.urlsafe_b64decode(data).decode('utf-8')
            elif 'parts' in part:  # Handle nested parts
                body += get_email_body(part)
    elif payload['mimeType'] == 'text/plain':
        data = payload['body'].get('data', '')
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8')
    return body


def fetch_unread_emails(max_results=30):
    """Fetches the most recent unread emails and formats them for the agent."""
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    
    # Search for unread emails in the inbox
    results = service.users().messages().list(userId='me', q='is:unread in:inbox', maxResults=max_results).execute()
    messages = results.get('messages', [])
    
    parsed_emails = []
    
    if not messages:
        return parsed_emails

    for msg in messages:
        # Fetch the full email payload
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        payload = msg_data['payload']
        headers = payload.get('headers', [])
        
        # Extract metadata
        sender = next((header['value'] for header in headers if header['name'].lower() == 'from'), 'Unknown Sender')
        subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'No Subject')
        
        # Extract and clean body
        body = get_email_body(payload)
        
        # Fallback if no text/plain is found (e.g., purely HTML emails)
        if not body:
            body = "HTML or Non-Text Payload. Body skipped for triage."
            
        parsed_emails.append({
            "id": msg['id'],
            "sender": sender,
            "subject": subject,
            "body": body.strip()
        })
        
    return parsed_emails

if __name__ == "__main__":
    print("Fetching up to 30 unread emails from your inbox...\n")
    live_emails = fetch_unread_emails(max_results=5) # Kept at 5 just for a quick test
    
    if not live_emails:
        print("Your inbox is empty! No unread emails found.")
    
    for idx, email in enumerate(live_emails, 1):
        print(f"--- Email {idx} ---")
        print(f"From   : {email['sender']}")
        print(f"Subject: {email['subject']}")
        print(f"Snippet: {email['body'][:100]}...\n")