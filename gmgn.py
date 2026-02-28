import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

DEFINED_API_KEY = os.getenv("CODEX_DEFINED_API_KEY")

def get_trending_tokens():
    """Fetch early gem Solana tokens - small mcap, new, with buy pressure"""
    
    url = "https://graph.codex.io/graphql"
    headers = {
        "Content-Type": "application/json",
        "Authorization": DEFINED_API_KEY
    }
    
    query = """
{
  filterTokens(
    filters: {
      network: [1399811149]
      liquidity: { gt: 500 }
      circulatingMarketCap: { gt: 1000, lt: 50000000 }
    }
    rankings: {
      attribute: volumeChange1
      direction: DESC
    }
    limit: 50
  ) {
    results {
      buyVolume1
      sellVolume1
      circulatingMarketCap
      liquidity
      txnCount1
      holders
      token {
        info {
          address
          name
          symbol
        }
        createdAt
      }
    }
  }
}
"""
    
    try:
        response = requests.post(url, json={"query": query}, headers=headers, timeout=10)
        data = response.json()
        
        if "errors" in data:
            print(f"GraphQL errors: {data['errors']}")
            return []
        
        filter_result = data.get("data", {}).get("filterTokens")
        if not filter_result:
            print(f"No filterTokens in response: {data.get('data')}")
            return []
        
        tokens = []
        for item in filter_result.get("results", []):
            buy = float(item.get("buyVolume1") or 0)
            sell = float(item.get("sellVolume1") or 0)
            created_at = item["token"].get("createdAt")
            age_hours = round((time.time() - created_at) / 3600, 1) if created_at else None
            
            tokens.append({
                "symbol": item["token"]["info"]["symbol"],
                "name": item["token"]["info"]["name"],
                "address": item["token"]["info"]["address"],
                "buy_volume_1h": buy,
                "sell_volume_1h": sell,
                "buy_sell_ratio": round(buy / sell, 2) if sell > 0 else 0,
                "market_cap": float(item.get("circulatingMarketCap") or 0),
                "liquidity": float(item.get("liquidity") or 0),
                "txn_count_1h": item.get("txnCount1", 0),
                "holders": item.get("holders", 0),
                "age_hours": age_hours,
            })
        
        # Debug prints
        print(f"🔍 Raw tokens before filtering: {len(tokens)}")
        for t in tokens:
            print(f"   {t['symbol']} | ratio: {t['buy_sell_ratio']} | buy_vol: {t['buy_volume_1h']} | holders: {t['holders']} | age: {t['age_hours']}h")
        
        # Rocket: ≤2h + significant volume
        rocket = [t for t in tokens if t["age_hours"] is not None and t["age_hours"] <= 2 and t["buy_volume_1h"] >= 5000]
        # Young: ≤24h with buy pressure
        young  = [t for t in tokens if t["age_hours"] is not None and t["age_hours"] <= 24 and t["buy_sell_ratio"] >= 0.9 and t["buy_volume_1h"] >= 150]
        # Mature: ≤7d with decent signal
        mature = [t for t in tokens if t["age_hours"] is not None and t["age_hours"] <= 168 and t["buy_sell_ratio"] >= 1.1 and t["buy_volume_1h"] >= 300]
        
        # Merge and deduplicate
        tokens = list({t["address"]: t for t in rocket + young + mature}.values())
        print(f"   After smart filter: {len(tokens)} (rocket ≤2h: {len(rocket)}, young ≤24h: {len(young)}, mature ≤7d: {len(mature)})")
        
        tokens = sorted(tokens, key=lambda x: x["buy_sell_ratio"], reverse=True)
        return tokens
    
    except Exception as e:
        print(f"Error: {e}")
        return []