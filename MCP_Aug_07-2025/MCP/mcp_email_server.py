import os
import base64
import logging
from dotenv import load_dotenv
from typing import List, Dict, Any

import googleapiclient.discovery
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from mcp.server.fastmcp import FastMCP

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("MCP email server", port=8000)

# Suppress Google API discovery cache warning
googleapiclient.discovery.DISABLE_CACHE = True

# Gmail API setup
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CREDS_FILE = os.getenv('GMAIL_CREDS_FILE', 'credentials.json')
TOKEN_FILE = os.getenv('GMAIL_TOKEN_FILE', 'token.json')

def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)


@mcp.tool()
async def get_unread_emails() -> List[Dict[str, Any]]:
    """Fetches unread emails from Gmail."""
    logger.info("get_unread_emails task invoked")
    try:
        service = get_gmail_service()
        results = service.users().messages().list(userId='me', q='is:unread', maxResults=10).execute()
        messages = results.get('messages', [])
        logger.info(f"messages: {messages}")
        emails = []
        for msg in messages:
            email = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = {h['name']: h['value'] for h in email['payload']['headers']}
            emails.append({
                'id': msg['id'],
                'threadId': email['threadId'],
                'from': headers.get('From', ''),
                'subject': headers.get('Subject', ''),
                'snippet': email['snippet']
            })
        logger.info(f"Fetched {len(emails)} unread emails")
        return emails
    except Exception as e:
        logger.error(f"Error fetching unread emails: {str(e)}")
        raise
    
@mcp.tool()
async def send_reply_email(message_id: str, thread_id: str, to: str, subject: str, body: str) -> Dict[str, Any]:
    """Sends a reply to a Gmail thread."""
    try:
        service = get_gmail_service()
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        message['In-Reply-To'] = message_id
        message['References'] = message_id
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw, 'threadId': thread_id}
        ).execute()
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        logger.info(f"Sent reply to thread {thread_id}")
        return {'status': 'success', 'threadId': thread_id, 'messageId': sent_message['id']}
    except Exception as e:
        logger.error(f"Error sending reply email: {str(e)}")
        raise

@mcp.tool()
async def get_joke() -> str:
    """Get a random joke (mocked)."""
    # Pretend to call an open jokes API
    return "Why did the developer go broke? Because he used up all his cache!"

@mcp.tool()
async def get_crypto_price(symbol: str) -> str:
    """Get the current price of a cryptocurrency (mocked)."""
    # Pretend to call a crypto price API
    prices = {"BTC": "$67,000", "ETH": "$3,500", "DOGE": "$0.12"}
    price = prices.get(symbol.upper(), "$???")
    return f"The current price of {symbol.upper()} is {price}. (mocked)"

@mcp.tool()
async def get_quote() -> str:
    """Get a random inspirational quote (mocked)."""
    # Pretend to call a quotes API
    return "The best way to get started is to quit talking and begin doing. – Walt Disney"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")