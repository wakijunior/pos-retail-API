from urllib import response

import requests
from dotenv import load_dotenv
import os

load_dotenv()

elastic_api_key = os.getenv("ELASTIC_API_KEY")
FROM_EMAIL = os.getenv("email")

url = "https://api.elasticemail.com/v2/email/send"

def send_email(to_email, subject, body):
    data = {
        'from': FROM_EMAIL,
        'to': to_email,
        'subject': subject,
        'bodyText': body,
        'apikey': elastic_api_key
    }
    response = requests.post(url, data=data)
    print(response.status_code)
    return response.json()
print(send_email(to_email='hewstechcomps@gmail.com', subject='Test Email', body='This is a test email.'))

# import mailtrap as mt

# MAIL_TRAP_API_KEY = "4a08064f01912e9ffdefd1a352424f05"

# def send_email(to, subject, text):
#     mail = mt.Mail(
#         sender=mt.Address(email="hello@demomailtrap.co", name="Mailtrap Test"),
#         to=[mt.Address(email=to)],
#         subject=subject,
#         text=text,
#         category="Integration Test",
#     )

#     client = mt.MailtrapClient(token=MAIL_TRAP_API_KEY)
#     response = client.send(mail)

#     print(response)

# send_email("hewstechcomps@gmail.com", "Test Email", "This is a test email.")
