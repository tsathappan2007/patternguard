import requests
import os
import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("PATTERN_GUARD_RUN_NETWORK_TESTS") != "1",
    reason="set PATTERN_GUARD_RUN_NETWORK_TESTS=1 to run external provider checks"
)

def test_groq_endpoints():
    print("Testing Groq endpoint format...")
    # Test with dummy key to see error response from Groq
    test_key = "gsk_test1234567890"
    
    endpoints = [
        "https://api.groq.com/openai/v1/chat/completions",
        "https://api.groq.com/v1/chat/completions"
    ]
    
    for ep in endpoints:
        resp = requests.post(
            ep,
            headers={"Authorization": f"Bearer {test_key}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": "hi"}]},
            timeout=10
        )
        print(f"Endpoint: {ep} -> Status: {resp.status_code}, Response: {resp.text[:120]}")

if __name__ == "__main__":
    test_groq_endpoints()

