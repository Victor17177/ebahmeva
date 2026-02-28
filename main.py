import os
import sys
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from skills.scan import analyze_tokens
from tools.telegram import send_telegram

def main():
    print("=" * 50)
    print("🚀 SOLANA SMART MONEY SCANNER")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    while True:
        print()
        print(f"🔄 Scanning... {datetime.now().strftime('%H:%M:%S')}")
        
        report = analyze_tokens()

        if report:
            print(report)

            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write("SOLANA SMART MONEY REPORT\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                f.write(report)
            print(f"\n💾 Report saved to: {filename}")

            # Send to Telegram
            send_telegram(f"🚀 *SOLANA SMART MONEY SCANNER*\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{report}")

        else:
            print("😴 No early gems found right now.")

        print()
        print("⏳ Next scan in 5 minutes...")
        print("=" * 50)
        time.sleep(300)

if __name__ == "__main__":
    main()