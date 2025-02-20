# app/adapters/sms_provider.py
import requests
from app.settings import settings


def send_sms(phone_number: str, message: str):
    """
    Sends an SMS to the specified phone number using an SMS provider API.

    This function is an example of how to integrate with an SMS service. Currently,
    the actual API call is commented out. When active, it sends a POST request to the
    SMS API with the phone number, message, and API key.

    :param phone_number: The phone number to send the SMS to.
    :param message: The message content to send in the SMS.
    """
    # Example using an SMS provider API
    # payload = {
    #     "to": phone_number,
    #     "message": message,
    #     "api_key": settings.SMS_API_KEY,
    # }
    # response = requests.post(settings.SMS_API_URL, data=payload)

    # Uncomment the lines above to send the actual request when the provider is available.

    # if response.status_code == 200:
    #     print(f"SMS sent successfully to {phone_number}")
    # else:
    #     print(f"Failed to send SMS to {phone_number}")

    pass  # The function is currently not sending SMS, it's a placeholder.
