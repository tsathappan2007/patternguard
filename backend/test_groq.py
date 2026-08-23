import requests

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
            json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": "hi"}]}
        )
        print(f"Endpoint: {ep} -> Status: {resp.status_code}, Response: {resp.text[:120]}")

if __name__ == "__main__":
    test_groq_endpoints()

