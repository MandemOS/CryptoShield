import sys
import os
from dotenv import load_dotenv
from web3 import Web3

# Load environment variables from .env file
load_dotenv()
CHAINSTACK_URL = os.getenv("CHAINSTACK_ACCESS_KEY")

if not CHAINSTACK_URL:
    print("⚠️ Warning: CHAINSTACK_ACCESS_KEY not found in .env file!")
else:
    print(f"✅ Loaded Chainstack URL from .env")

# PancakeSwap Factory contract info for LP token lookup
PANCAKE_FACTORY_ADDRESS = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
PANCAKE_FACTORY_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "tokenA", "type": "address"},
            {"internalType": "address", "name": "tokenB", "type": "address"}
        ],
        "name": "getPair",
        "outputs": [{"internalType": "address", "name": "pair", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    }
]

WBNB_ADDRESS = "0xBB4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"

# Adjust sys.path to import your bots from their folders
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'HONEY TRACKER'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'RUG PULL TRACKER'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'LIQUID'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'LP'))

# Import your bot functions
from honeypot_detector import run_honeypot
from rug_pull_checker import run_rugpull
from liquidity_checker import run_liquidity
from lp_lock_checker import run_lp_lock_check


def get_lp_token_address(token_address, chainstack_url):
    """Get the PancakeSwap LP token address for token/WBNB pair"""
    try:
        w3 = Web3(Web3.HTTPProvider(chainstack_url))
        factory = w3.eth.contract(address=Web3.to_checksum_address(PANCAKE_FACTORY_ADDRESS), abi=PANCAKE_FACTORY_ABI)
        lp_address = factory.functions.getPair(Web3.to_checksum_address(token_address), Web3.to_checksum_address(WBNB_ADDRESS)).call()
        if lp_address == "0x0000000000000000000000000000000000000000":
            return None  # No LP pair found
        return lp_address
    except Exception as e:
        print(f"❌ Error getting LP token address: {e}")
        return None


def print_honeypot_report(result):
    print("[HONEYPOT CHECK]")
    if result.get("error"):
        print(f"❌ Honeypot check failed: {result['error']}")
        print("🚨 HONEYPOT DETECTED or transaction reverted - possible buy/sell failure.")
    else:
        buy_tokens = result.get("buy_tokens")
        sell_bnb_returned = result.get("sell_bnb_returned")
        slippage_tax_percent = result.get("slippage_tax_percent")
        passed = result.get("passed", True)
        messages = result.get("messages", [])

        if buy_tokens is not None and sell_bnb_returned is not None and slippage_tax_percent is not None:
            print(f"Buy: 0.01 BNB → {buy_tokens:.6f} tokens")
            print(f"Sell: {sell_bnb_returned:.6f} BNB returned")
            print(f"Slippage / Tax: {slippage_tax_percent:.2f}%")
        for msg in messages:
            print(msg)
        if not passed:
            print("❌ Honeypot detected or high tax.")
        else:
            print("✅ Looks safe: No Honeypot detected.")
    print("")


def print_rugpull_report(result):
    print("[RUG PULL CHECK]")
    if result.get("error"):
        print(f"❌ Rug Pull check failed: {result['error']}")
        print("🚨 Possible rug pull or scam detected: contract functions missing or reverted.")
    else:
        name = result.get("name", "Unknown")
        symbol = result.get("symbol", "Unknown")
        decimals = result.get("decimals", "Unknown")
        total_supply = result.get("total_supply", "Unknown")
        transfer_function_exists = result.get("transfer_function_exists", False)
        ownership_status = result.get("ownership_status", "unknown")
        ownership_owner = result.get("ownership_owner", "Unknown")
        messages = result.get("messages", [])

        print(f"Name: {name}")
        print(f"Symbol: {symbol}")
        print(f"Decimals: {decimals}")
        print(f"Total Supply: {total_supply}")

        if transfer_function_exists:
            print("✅ Transfer function exists: Token appears legitimate.")
        else:
            print("⚠️ No transfer function: Possible honeypot or scam.")

        if ownership_status == "renounced":
            print("✅ Ownership renounced.")
        elif ownership_status == "owned":
            print(f"⚠️ Ownership not renounced. Owner: {ownership_owner}")
        else:
            print("⚠️ Ownership status unknown.")

        for msg in messages:
            print(msg)
    print("")


def print_liquidity_report(result):
    print("[LIQUIDITY CHECK]")
    if result.get("error"):
        print(f"❌ Liquidity check failed: {result['error']}")
        print("🚨 No liquidity pool found or zero liquidity.")
    else:
        pair_address = result.get("pair_address", "Unknown")
        wbnb_reserve = result.get("wbnb_reserve", "Unknown")
        token_reserve = result.get("token_reserve", "Unknown")
        low_wbnb_reserve = result.get("low_wbnb_reserve", False)
        low_token_reserve = result.get("low_token_reserve", False)
        messages = result.get("messages", [])

        print(f"Liquidity Pool Address: {pair_address}")
        print(f"WBNB Reserve: {wbnb_reserve} BNB")
        print(f"Token Reserve: {token_reserve} Tokens")

        if low_wbnb_reserve:
            print("⚠️ Warning: WBNB reserve too low! Potential slippage.")
        if low_token_reserve:
            print("⚠️ Warning: Token reserve too low! Low liquidity.")

        for msg in messages:
            print(msg)
    print("")


def print_lp_lock_report(results):
    print("[LP LOCK CHECK]")
    if not results:
        print("⚠️ No LP locks found or all checks failed.")
    else:
        for res in results:
            if "error" in res:
                print(f"❌ {res['locker']} - Error: {res['error']}")
            else:
                if res.get("locked_amount", 0) > 0:
                    print(f"✅ {res['locker']} - {res['locked_amount']} tokens locked until {res['unlocks_at']}")
                else:
                    print(f"⚠️ {res['locker']} - No tokens locked.")
    print("")


def calculate_score(honeypot_result, rugpull_result, liquidity_result):
    score = 0

    if honeypot_result.get("passed") and not honeypot_result.get("error"):
        score += 3

    if not rugpull_result.get("error"):
        if rugpull_result.get("transfer_function_exists"):
            score += 2
        if rugpull_result.get("ownership_status") == "renounced":
            score += 1

    if not liquidity_result.get("error"):
        if not liquidity_result.get("low_wbnb_reserve"):
            score += 2
        if not liquidity_result.get("low_token_reserve"):
            score += 2

    return score


def main():
    while True:
        token = input("\nEnter token address (0x...) or type 'exit' to quit: ").strip()
        if token.lower() == 'exit':
            print("🛑 Exiting Crypto Shield.")
            break

        if not token.startswith("0x") or len(token) != 42:
            print("❌ Invalid token address format. Try again.")
            continue

        print(f"\n🚀 Running Crypto Shield checks on token: {token}\n")

        try:
            honeypot_result = run_honeypot(token)
        except Exception as e:
            honeypot_result = {"error": str(e), "passed": False, "messages": [str(e)]}
        print_honeypot_report(honeypot_result)

        try:
            rugpull_result = run_rugpull(token)
        except Exception as e:
            rugpull_result = {"error": str(e), "messages": [str(e)]}
        print_rugpull_report(rugpull_result)

        try:
            liquidity_result = run_liquidity(token)
        except Exception as e:
            liquidity_result = {"error": str(e), "messages": [str(e)]}
        print_liquidity_report(liquidity_result)

        try:
            # Get LP token address first
            lp_token_address = get_lp_token_address(token, CHAINSTACK_URL)
            if lp_token_address is None:
                lp_lock_result = [{"locker": "LP Lock Check", "error": "No LP token pair found"}]
            else:
                lp_lock_result = run_lp_lock_check(lp_token_address, chainstack_url=CHAINSTACK_URL)
        except Exception as e:
            lp_lock_result = [{"locker": "LP Lock Check", "error": str(e)}]
        print_lp_lock_report(lp_lock_result)

        # Scoring
        score = calculate_score(honeypot_result, rugpull_result, liquidity_result)
        print(f"\n🔐 CryptoShield Score for {token}: {score}/10")

        # Final verdict
        if score >= 7:
            print("✅ FINAL VERDICT: COIN PASSED — GOOD TO BUY")
        elif score >= 4:
            print("⚠️ FINAL VERDICT: COIN WARNING — PROCEED WITH CAUTION")
        else:
            print("❌ FINAL VERDICT: COIN FAILED — SCAM LIKELY")

        print("\n✅ Crypto Shield checks completed.")
        print("-" * 50)


if __name__ == "__main__":
    main()
