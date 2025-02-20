import random
import time
from typing import List, Dict


class SmsProvider:
    """
    Abstract base class for SMS Providers.
    All SMS provider classes should inherit from this and implement `send_otp` method.
    """

    async def send_otp(self, phone_number: str, otp_code: str) -> str:
        """
        Method to send OTP to the given phone number.

        Args:
            phone_number (str): The phone number to which the OTP should be sent.
            otp_code (str): The OTP code to send.

        Returns:
            str: A message indicating the OTP sent, if successful.

        Raises:
            NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError


class SmsIR(SmsProvider):
    """
    A specific SMS provider implementation for SmsIR service.
    """

    async def send_otp(self, phone_number: str, otp_code: str) -> str:
        """
        Simulates sending OTP using SmsIR. Randomly fails or succeeds.

        Args:
            phone_number (str): The phone number to which the OTP should be sent.
            otp_code (str): The OTP code to send.

        Returns:
            str: A message indicating success or failure.

        Raises:
            Exception: If sending OTP fails.
        """
        success = random.choice([True, False])
        if not success:
            raise Exception("SmsIR failed")
        result = f"SmsIR used for OTP: {otp_code}"
        return result


class KaveNegar(SmsProvider):
    """
    A specific SMS provider implementation for KaveNegar service.
    """

    async def send_otp(self, phone_number: str, otp_code: str) -> str:
        """
        Simulates sending OTP using KaveNegar. Randomly fails or succeeds.

        Args:
            phone_number (str): The phone number to which the OTP should be sent.
            otp_code (str): The OTP code to send.

        Returns:
            str: A message indicating success or failure.

        Raises:
            Exception: If sending OTP fails.
        """
        success = random.choice([True, False])
        if not success:
            raise Exception("KaveNegar failed")
        result = f"KaveNegar used for OTP: {otp_code}"
        return result


class Signal(SmsProvider):
    """
    A specific SMS provider implementation for Signal service.
    """

    async def send_otp(self, phone_number: str, otp_code: str) -> str:
        """
        Simulates sending OTP using Signal. Randomly fails or succeeds.

        Args:
            phone_number (str): The phone number to which the OTP should be sent.
            otp_code (str): The OTP code to send.

        Returns:
            str: A message indicating success or failure.

        Raises:
            Exception: If sending OTP fails.
        """
        success = random.choice([True, False])
        if not success:
            raise Exception("Signal failed")
        result = f"Signal used for OTP: {otp_code}"
        return result


class CircuitBreaker:
    """
    Circuit Breaker pattern to prevent repeated failures from a service provider.
    Tracks failures and provides a mechanism to prevent further attempts for a certain time.
    """

    def __init__(self, failure_threshold: int, reset_time: int):
        """
        Initializes the CircuitBreaker with given failure threshold and reset time.

        Args:
            failure_threshold (int): Maximum number of failures before a provider is 'blocked'.
            reset_time (int): Time (in seconds) before the failure count is reset for a provider.
        """
        self.failure_threshold = failure_threshold
        self.reset_time = reset_time
        self.failures: Dict[str, int] = {}
        self.last_failure_time: Dict[str, float] = {}

    def can_attempt(self, provider_name: str) -> bool:
        """
        Checks if a provider can be used for sending OTP based on failure history.

        Args:
            provider_name (str): The name of the provider to check.

        Returns:
            bool: `True` if the provider can be used, `False` otherwise.
        """
        if provider_name not in self.failures:
            return True
        if self.failures[provider_name] < self.failure_threshold:
            return True
        if time.time() - self.last_failure_time[provider_name] > self.reset_time:
            self.failures[provider_name] = 0
            return True
        return False

    def record_failure(self, provider_name: str):
        """
        Records a failure for a provider and logs the time of failure.

        Args:
            provider_name (str): The provider for which the failure is recorded.
        """
        self.failures[provider_name] = self.failures.get(provider_name, 0) + 1
        self.last_failure_time[provider_name] = time.time()


class SmsService:
    """
    Service that manages multiple SMS providers for sending OTPs.
    Uses the Circuit Breaker to handle provider failures and rotates providers if necessary.
    """

    def __init__(self, providers: List[SmsProvider]):
        """
        Initializes the SmsService with a list of SMS providers and a CircuitBreaker.

        Args:
            providers (List[SmsProvider]): List of SMS providers to be used.
        """
        self.providers = providers
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, reset_time=60)
        self.current_index = 0

    async def send_otp(self, phone_number: str, otp_code: str) -> str:
        """
        Attempts to send OTP through each provider in the list, rotating through them.
        If one provider fails, it moves to the next, and uses the CircuitBreaker to prevent
        repeated failures.

        Args:
            phone_number (str): The phone number to which the OTP should be sent.
            otp_code (str): The OTP code to send.

        Returns:
            str: A message indicating which provider sent the OTP, or failure message.

        Raises:
            Exception: If all providers fail.
        """
        for _ in range(len(self.providers)):
            provider = self.providers[self.current_index]
            provider_name = provider.__class__.__name__

            if self.circuit_breaker.can_attempt(provider_name):
                try:
                    otp_sent = await provider.send_otp(phone_number, otp_code)
                    if otp_sent:
                        return otp_sent
                except Exception:
                    self.circuit_breaker.record_failure(provider_name)

            # Rotate to the next provider
            self.current_index = (self.current_index + 1) % len(self.providers)

        raise Exception("All providers failed")
