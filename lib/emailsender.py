import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os

from utils.logs import generatelogs

logging.basicConfig(level=logging.INFO)
# Set up logging
def logging_generate(messagetype, message, filelocation):
    log_message = f"{messagetype}: {message} (Logged from {filelocation})"
    logging.info(log_message)
    generatelogs(messagetype,message,filelocation)
    

def email_sender(email, subject, text):
    try:
        smtp_host = 'smtp.hostinger.com'
        smtp_port = 465  # Port for SSL
        sender_email = os.getenv('HOSTINGER_EMAIL')  
        
        sender_password = os.getenv('HOSTINGER_PASS')
        
        
        # Set up the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(text, 'plain'))
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
        messagetype = "success"
        message = f"Email sent successfully to {email} with message {message} and filelocation - {filelocation}"
        filelocation = "emailsender.py"
        logging_generate(messagetype, message, filelocation)
        
        print(f"Email sent successfully to {email}")
    
    except Exception as e:
        messagetype = "error"
        message = f"Failed to send email and the reason is: {str(e)}"
        filelocation = "emailcreator.py"
        logging_generate(messagetype, message, filelocation)
        print(f"Error sending email to {email}: {e}")
        raise Exception(f"Failed to send email and the reason is: {str(e)}")