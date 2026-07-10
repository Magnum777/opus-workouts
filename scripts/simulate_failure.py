#!/usr/bin/env python3
"""Simulate a flaky external API and verify retry + circuit-breaker logic."""
import random, time

class FlakyAPI:
    def __init__(self, fail_rate=0.6):
        self.fail_rate = fail_rate
        self.calls = 0

    def call(self):
        self.calls += 1
        if random.random() < self.fail_rate:
            raise ConnectionError(f"Simulated timeout (call #{self.calls})")
        return {"status": "ok", "data": [1, 2, 3]}

def retry_with_backoff(func, max_retries=3, base_delay=1.0):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait = base_delay * (2 ** attempt)
            print(f"  Retry {attempt+1}/{max_retries} after {wait}s: {e}")
            time.sleep(wait)

class CircuitBreaker:
    def __init__(self, threshold=3, cooldown=10):
        self.failures = 0
        self.threshold = threshold
        self.cooldown = cooldown
        self.last_failure = 0

    def call(self, func):
        if self.failures >= self.threshold:
            if time.time() - self.last_failure < self.cooldown:
                raise RuntimeError("Circuit OPEN — rejecting calls")
            self.failures = 0  # half-open
        try:
            result = func()
            self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()
            raise

if __name__ == "__main__":
    api = FlakyAPI(fail_rate=0.5)
    cb = CircuitBreaker(threshold=3, cooldown=5)

    for i in range(10):
        try:
            result = cb.call(lambda: retry_with_backoff(api.call, max_retries=2))
            print(f"Call {i+1}: SUCCESS — {result}")
        except Exception as e:
            print(f"Call {i+1}: FAILED — {e}")
        time.sleep(0.5)
