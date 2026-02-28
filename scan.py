from groq import Groq
import os
import sys
import json
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.gmgn import get_trending_tokens

load_dotenv()

def categorize_token(t):
    if t["age_hours"] is not None and t["age_hours"] <= 2 and t["buy_volume_1h"] >= 10000:
        return "🚀 ROCKET (< 2h old)"
    elif t["age_hours"] is not None and t["age_hours"] <= 24:
        return "🌱 YOUNG (< 24h old)"
    else:
        return "📈 MATURE (< 7 days old)"

def analyze_tokens():
    """Fetch token data and analyze with Groq"""
    
    print("📡 Fetching Solana token data...")
    tokens = get_trending_tokens()
    
    if not tokens:
        print("No tokens found.")
        return
    
    # Tag each token with its category
    for t in tokens:
        t["category"] = categorize_token(t)
    
    token_summary = json.dumps(tokens, indent=2)
    
    # Read agent instructions
    agent_md_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agent.md")
    with open(agent_md_path, "r", encoding="utf-8") as f:
        agent_instructions = f.read()
    
    print("🤖 Sending data to Groq for analysis...\n")
    
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": agent_instructions
            },
            {
                "role": "user",
                "content": f"Here is the current Solana token data with categories. Please analyze it and give me your report:\n\n{token_summary}"
            }
        ],
        max_tokens=1024
    )
    
    report = response.choices[0].message.content
    # Append token addresses
    address_lines = "\n\n📋 *Token Addresses:*"
    for t in tokens:
        address_lines += f"\n• {t['symbol']}: `{t['address']}`"
    return report + address_lines

if __name__ == "__main__":
    analyze_tokens()