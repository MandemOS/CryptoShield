# llm_helper.py - 100% WORKING VERSION
import os
import sys
from pathlib import Path

# MANUAL OPENAI CLIENT IMPLEMENTATION
class SimpleOpenAIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
        
    def chat_completions_create(self, **kwargs):
        import requests
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=kwargs,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

# LOAD ENV FILE
env_path = Path(__file__).parent / "envfile.txt"
if not env_path.exists():
    raise FileNotFoundError(f"""
    🔴 CRITICAL: envfile.txt missing at {env_path}
    Directory contents:
    {[f.name for f in env_path.parent.iterdir() if f.is_file()]}
    """)

# LOAD API KEY
from dotenv import load_dotenv
load_dotenv(env_path)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError(f"""
    🔴 Invalid envfile.txt at {env_path}
    Contents: {env_path.read_text()}
    Required format: OPENAI_API_KEY=your_key_here
    """)

# INIT CLIENT
client = SimpleOpenAIClient(api_key)

def explain_token_score(score, honeypot_passed, rugpull_passed, liquidity_status):
    """Direct API implementation that bypasses all package issues"""
    try:
        result = client.chat_completions_create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"""
                Token Security (1 line):
                Honeypot: {'✅' if honeypot_passed else '❌'}
                Rugpull: {'✅' if rugpull_passed else '❌'} 
                Liquidity: {'✅' if liquidity_status == 'Sufficient' else '⚠️'}
                Score: {score}/100
                """
            }],
            temperature=0.7,
            max_tokens=100
        )
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"⚠️ Analysis skipped: {str(e)[:100]}"

# VERIFICATION
if __name__ == "__main__":
    print("🔹 TEST OUTPUT:")
    print(explain_token_score(85, True, False, "Low"))
