# app/adapters/sms_provider.py
import requests
from app.settings import settings


def send_sms(phone_number: str, message: str):
    # Example using an SMS provider API
    # payload = {
    #     "to": phone_number,
    #     "message": message,
    #     "api_key": settings.SMS_API_KEY,
    # }
    # response = requests.post(settings.SMS_API_URL, data=payload)
    # if response.status_code == 200:
    #     print(f"SMS sent successfully to {phone_number}")
    # else:
    #     print(f"Failed to send SMS to {phone_number}")
    pass
