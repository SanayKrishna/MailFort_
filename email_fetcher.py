import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv() 
def fetch_latest_emails(num_emails=5):
   
    try:
    
        USER = os.getenv("EMAIL_USER")
        PASSWORD = os.getenv("EMAIL_PASS")
        IMAP_SERVER = os.getenv("IMAP_SERVER")

        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(USER, PASSWORD)

        mail.select("inbox")

        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()
        latest_email_ids = email_ids[-num_emails:]

        email_list = []

        for email_id in reversed(latest_email_ids):
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")

                    from_ = msg.get("From")

                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                try:
                                    body = part.get_payload(decode=True).decode()
                                except:
                                    pass
                                break
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode()
                        except:
                            pass
                    
                    email_list.append({"from": from_, "subject": subject, "body": body})
        
        mail.logout()
        return email_list

    except Exception as e:
        print(f"Error connecting to email: {e}")
        return []

if __name__ == '__main__':
    emails = fetch_latest_emails(3)
    for i, email_data in enumerate(emails):
        print(f"--- EMAIL {i+1} ---")
        print(f"From: {email_data['from']}")
        print(f"Subject: {email_data['subject']}")
        print(f"Body: {email_data['body'][:100]}...") 
        print("\n")