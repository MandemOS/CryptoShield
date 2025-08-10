import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'honey_tracker'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'rug_pull_tracker'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'liquid'))

from honey_tracker import run_honeypot_detector
from rug_pull_tracker import run_rug_pull_checker
from liquidity_tracker import run_liquidity_checker

def calculate_score(honey_result, rug_result, liquid_result):
    score = 0

    # Adjust the scoring based on keywords detected in each bot result
    if honey_result and ("No honeypot" in honey_result or "✅" in honey_result):
        score += 3
    if rug_result and ("No rug functions" in rug_result or "✅" in rug_result):
        score += 3
    if liquid_result and ("Sufficient liquidity" in liquid_result or "✅" in liquid_result):
        score += 4

    return score

def main():
    print("\n🛡️  Welcome to CryptoShield\n")
    token_address = input("🔍 Enter token address to scan: ").strip()

    print("\nRunning Honeypot Detector...\n")
    honey_result = run_honeypot_detector(token_address)
    print(honey_result)

    print("\nRunning Rug Pull Checker...\n")
    rug_result = run_rug_pull_checker(token_address)
    print(rug_result)

    print("\nRunning Liquidity Checker...\n")
    liquid_result = run_liquidity_checker(token_address)
    print(liquid_result)

    score = calculate_score(honey_result, rug_result, liquid_result)
    print(f"\n🔐 CryptoShield Score for {token_address}: {score}/10\n")

if __name__ == "__main__":
    main()
