import random
import time
from typing import List, Dict


class SmsProvider:
    async def send_otp(self, phone_number: str, otp_code: str) -> str:
        raise NotImplementedError


class SmsIR(SmsProvider):
    async def send_otp(self, phone_number: str, otp_code: str) -> str:
        # simulate success or failure
        success = random.choice([True, False])
        if not success:
            raise Exception("SmsIR failed")
        result = f"SmsIR used for OTP: {otp_code}"
        return result


class KaveNegar(SmsProvider):
    async def send_otp(self, phone_number: str, otp_code: str) -> str:
        success = random.choice([True, False])
        if not success:
            raise Exception("KaveNegar failed")
        result = f"KaveNegar used for OTP: {otp_code}"
        return result


class Signal(SmsProvider):
    async def send_otp(self, phone_number: str, otp_code: str) -> str:
        success = random.choice([True, False])
        if not success:
            raise Exception("Signal failed")
        result = f"Signal used for OTP: {otp_code}"
        return result


class CircuitBreaker:
    def __init__(self, failure_threshold: int, reset_time: int):
        self.failure_threshold = failure_threshold
        self.reset_time = reset_time
        self.failures: Dict[str, int] = {}
        self.last_failure_time: Dict[str, float] = {}

    def can_attempt(self, provider_name: str) -> bool:
        if provider_name not in self.failures:
            return True
        if self.failures[provider_name] < self.failure_threshold:
            return True
        if time.time() - self.last_failure_time[provider_name] > self.reset_time:
            self.failures[provider_name] = 0
            return True
        return False

    def record_failure(self, provider_name: str):
        self.failures[provider_name] = self.failures.get(provider_name, 0) + 1
        self.last_failure_time[provider_name] = time.time()


class SmsService:
    def __init__(self, providers: List[SmsProvider]):
        self.providers = providers
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, reset_time=60)
        self.current_index = 0

    async def send_otp(self, phone_number: str, otp_code: str) -> str:
        for _ in range(len(self.providers)):
            provider = self.providers[self.current_index]
            provider_name = provider.__class__.__name__

            if self.circuit_breaker.can_attempt(provider_name):
                # try:
                otp_sent = await provider.send_otp(phone_number, otp_code)
                if otp_sent:
                    return otp_sent
                # except Exception:
                #     self.circuit_breaker.record_failure(provider_name)

            self.current_index = (self.current_index + 1) % len(self.providers)

        raise Exception("All providers failed")
