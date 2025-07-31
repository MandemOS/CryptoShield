# CryptoShield
AI-powered multi-chain crypto risk detection and analysis platform.
# CryptoShield

CryptoShield is an AI-powered multi-chain cryptocurrency risk detection platform designed to identify honeypots, rug pulls, and other scams in real-time. It aims to make DeFi investing safer by providing clear, actionable insights to users of all experience levels.

## Features
- Real-time token risk analysis across BSC, Ethereum, and Polygon  
- Advanced honeypot and rug pull detection algorithms  
- AI-driven natural language explanations of complex risks  
- User-friendly interface and API integration  

## Getting Started
1. Clone the repo: `git clone https://github.com/yourusername/cryptoshield.git`  
2. Install dependencies: `pip install -r requirements.txt`  
3. Run the main analysis script: `python main.py`

## License
This project is licensed under the MIT License.

Honeypot tracker 
from web3 import Web3
import json
import os

def run_honeypot(token_address: str):
    result = {
        "buy_tokens": None,
        "sell_bnb_returned": None,
        "slippage_tax_percent": None,
        "passed": True,
        "messages": [],
        "error": None,
    }

    # Load ABI from file
    abi_path = os.path.join(os.path.dirname(__file__), "honeypancake_router_abi.json")
    try:
        with open(abi_path, "r") as abi_file:
            ROUTER_ABI = json.load(abi_file)
    except Exception as e:
        result["error"] = f"Failed to load Router ABI: {e}"
        result["passed"] = False
        result["messages"].append(result["error"])
        return result

    # Connect to BSC
    BSC_RPC = "https://bsc-dataseed.binance.org/"
    web3 = Web3(Web3.HTTPProvider(BSC_RPC))

    if not web3.is_connected():
        result["error"] = "Failed to connect to BSC network"
        result["passed"] = False
        result["messages"].append(result["error"])
        return result

    # PancakeSwap Router V2 address
    ROUTER_ADDRESS = Web3.to_checksum_address("0x10ED43C718714eb63d5aA57B78B54704E256024E")
    router = web3.eth.contract(address=ROUTER_ADDRESS, abi=ROUTER_ABI)

    WBNB = Web3.to_checksum_address("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")

    try:
        token_address = Web3.to_checksum_address(token_address)

        # Define paths for trade simulation
        path = [WBNB, token_address]
        reverse_path = [token_address, WBNB]

        # Simulate BUY: 0.01 BNB
        bnb_amount = web3.to_wei(0.01, 'ether')
        tokens_out = router.functions.getAmountsOut(bnb_amount, path).call()
        token_amount = tokens_out[1]

        # Simulate SELL
        bnb_back = router.functions.getAmountsOut(token_amount, reverse_path).call()[1]

        buy_tax = ((bnb_amount - bnb_back) / bnb_amount) * 100

        result["buy_tokens"] = token_amount / 10**18
        result["sell_bnb_returned"] = bnb_back / 10**18
        result["slippage_tax_percent"] = buy_tax

        if bnb_back == 0 or buy_tax > 40:
            result["passed"] = False
            result["messages"].append("🚨 Possible Honeypot or High Tax Detected!")
        else:
            result["messages"].append("✅ Looks safe: No Honeypot detected.")

    except Exception as e:
        result["error"] = f"Error checking token: {e}"
        result["passed"] = False
        result["messages"].append(result["error"])

    return result

    rug pull detector 
    import json
from web3 import Web3
import os

def run_rugpull(token_address: str):
    result = {
        "name": None,
        "symbol": None,
        "decimals": None,
        "total_supply": None,
        "transfer_function_exists": False,
        "ownership_status": None,  # "renounced", "owned", or "unknown"
        "ownership_owner": None,
        "error": None,
        "passed": True,
        "messages": []
    }

    # Connect to BSC
    http_provider = "https://bsc-dataseed.binance.org/"
    web3 = Web3(Web3.HTTPProvider(http_provider))

    # Load ERC20 ABI
    abi_path = os.path.join(os.path.dirname(__file__), "RUGIERC20_ABI.json")
    try:
        with open(abi_path) as f:
            erc20_abi = json.load(f)
    except Exception as e:
        result["error"] = f"Failed to load ERC20 ABI: {e}"
        result["passed"] = False
        result["messages"].append(result["error"])
        return result

    try:
        token_address = Web3.to_checksum_address(token_address)
        token_contract = web3.eth.contract(address=token_address, abi=erc20_abi)

        # Basic token info
        result["name"] = token_contract.functions.name().call()
        result["symbol"] = token_contract.functions.symbol().call()
        result["decimals"] = token_contract.functions.decimals().call()
        total_supply_raw = token_contract.functions.totalSupply().call()
        result["total_supply"] = total_supply_raw / (10 ** result["decimals"])

        # Transfer function check
        try:
            token_contract.get_function_by_name("transfer")
            result["transfer_function_exists"] = True
        except Exception:
            result["transfer_function_exists"] = False
            result["passed"] = False
            result["messages"].append("⚠️ No transfer function: Possible scam or broken token.")

        # Ownership check
        try:
            owner_function = token_contract.get_function_by_name("owner")
            owner_address = owner_function().call()
            result["ownership_owner"] = owner_address

            # Check zero address for renounced ownership
            if owner_address == "0x0000000000000000000000000000000000000000":
                result["ownership_status"] = "renounced"
            else:
                result["ownership_status"] = "owned"
                result["passed"] = False
                result["messages"].append(f"⚠️ Contract ownership NOT renounced. Owner: {owner_address}")
        except Exception:
            # No owner() function available
            result["ownership_status"] = "unknown"
            result["messages"].append("⚠️ Ownership check not available on this token.")

    except Exception as e:
        result["error"] = f"Error checking token: {e}"
        result["passed"] = False
        result["messages"].append(result["error"])

    return result
    
Liquidity checker
from web3 import Web3
import json
import os

def run_liquidity(token_address: str):
    result = {
        "pair_address": None,
        "wbnb_reserve": None,
        "token_reserve": None,
        "low_wbnb_reserve": False,
        "low_token_reserve": False,
        "error": None,
        "passed": True,
        "messages": []
    }

    # Connect to BSC
    bsc_rpc = "https://bsc-dataseed.binance.org/"
    web3 = Web3(Web3.HTTPProvider(bsc_rpc))

    if not web3.is_connected():
        result['error'] = "Failed to connect to the blockchain."
        result['passed'] = False
        result['messages'].append(result['error'])
        return result

    # Load factory and pair ABIs
    try:
        factory_abi_path = os.path.join(os.path.dirname(__file__), 'liquid_pancake_factory_abi.json')
        pair_abi_path = os.path.join(os.path.dirname(__file__), 'liquid_pancake_pair_abi.json')
        with open(factory_abi_path) as f:
            factory_abi = json.load(f)
        with open(pair_abi_path) as f:
            pair_abi = json.load(f)
    except Exception as e:
        result['error'] = f"Error loading ABI files: {e}"
        result['passed'] = False
        result['messages'].append(result['error'])
        return result

    factory_address = Web3.to_checksum_address("0xca143ce32fe78f1f7019d7d551a6402fc5350c73")
    factory = web3.eth.contract(address=factory_address, abi=factory_abi)

    wbnb_address = Web3.to_checksum_address("0xBB4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")

    try:
        token_address = Web3.to_checksum_address(token_address)
        token0, token1 = sorted([wbnb_address, token_address])

        pair_address = factory.functions.getPair(token0, token1).call()
        if int(pair_address, 16) == 0:
            result['error'] = "No liquidity pool found for this token and WBNB."
            result['passed'] = False
            result['messages'].append(result['error'])
            return result

        pair = web3.eth.contract(address=pair_address, abi=pair_abi)
        reserves = pair.functions.getReserves().call()
        reserve0, reserve1, _ = reserves

        if token0.lower() == wbnb_address.lower():
            wbnb_reserve = reserve0
            token_reserve = reserve1
        else:
            wbnb_reserve = reserve1
            token_reserve = reserve0

        # Convert from Wei to Ether units (float)
        wbnb_reserve_float = web3.from_wei(wbnb_reserve, 'ether')
        token_reserve_float = web3.from_wei(token_reserve, 'ether')

        # Threshold checks
        low_wbnb_reserve = wbnb_reserve < 100 * 10**18  # <100 BNB
        low_token_reserve = token_reserve < 100 * 10**18  # <100 tokens (assuming 18 decimals)

        result.update({
            "pair_address": pair_address,
            "wbnb_reserve": float(wbnb_reserve_float),
            "token_reserve": float(token_reserve_float),
            "low_wbnb_reserve": low_wbnb_reserve,
            "low_token_reserve": low_token_reserve
        })

    except Exception as e:
        result['error'] = f"Error fetching liquidity: {e}"
        result['passed'] = False
        result['messages'].append(result['error'])

    return result

  LP checker 
  import json
from web3 import Web3

def run_lp_lock_check(token_address, chainstack_url):
    """
    Check LP token lock status on Unicrypt locker using Chainstack URL dynamically.
    Returns a list of dictionaries with locker name, locked amount, unlock time, or error.
    """

    UNICRYPT_LOCKER_ADDRESS = "0x7229247bD5cf29FA9B0764Aa1568732be024084b"

    # Unicrypt V2 LP Locker ABI (only needed functions)
    UNICRYPT_LOCKER_ABI = [
        {
            "constant": True,
            "inputs": [{"name": "_lpToken", "type": "address"}],
            "name": "getNumLocksForToken",
            "outputs": [{"name": "", "type": "uint256"}],
            "type": "function",
        },
        {
            "constant": True,
            "inputs": [{"name": "_lpToken", "type": "address"}, {"name": "_index", "type": "uint256"}],
            "name": "getLockForTokenAtIndex",
            "outputs": [
                {"name": "lockDate", "type": "uint256"},
                {"name": "amountLocked", "type": "uint256"},
                {"name": "unlockDate", "type": "uint256"},
                {"name": "owner", "type": "address"},
            ],
            "type": "function",
        }
    ]

    try:
        # Initialize Web3 with Chainstack RPC URL
        w3 = Web3(Web3.HTTPProvider(chainstack_url))
        if not w3.is_connected():
            return [{"locker": "UnicryptV2", "error": "Web3 connection failed"}]

        locker = w3.eth.contract(address=Web3.to_checksum_address(UNICRYPT_LOCKER_ADDRESS), abi=UNICRYPT_LOCKER_ABI)

        lp_token_checksum = Web3.to_checksum_address(token_address)
        num_locks = locker.functions.getNumLocksForToken(lp_token_checksum).call()

        if num_locks == 0:
            return [{"locker": "UnicryptV2", "locked_amount": 0, "unlocks_at": None}]

        # Check all locks
        results = []
        for i in range(num_locks):
            lock = locker.functions.getLockForTokenAtIndex(lp_token_checksum, i).call()
            lock_amount = w3.from_wei(lock[1], 'ether')
            unlock_time = lock[2]
            results.append({
                "locker": "UnicryptV2",
                "locked_amount": float(lock_amount),
                "unlocks_at": unlock_time
            })

        return results

    except Exception as e:
        return [{"locker": "UnicryptV2", "error": f"Error: {str(e)}"}]

      Whale monitor 
      from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import time

# ✅ Chainstack endpoint (BSC)
bsc_rpc = "https://bsc-mainnet.core.chainstack.com/"
web3 = Web3(Web3.HTTPProvider(bsc_rpc))

# ✅ Inject middleware for BSC (PoA)
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

if web3.is_connected():
    print("✅ Connected to BSC via Chainstack")
else:
    print("❌ Failed to connect to BSC")
    exit()

# ✅ Load ABIs
try:
    with open('wale_erc20_abi.json') as f:
        erc20_abi = json.load(f)
    with open('wale_pancake_router_abi.json') as f:
        router_abi = json.load(f)
except Exception as e:
    print("❌ Error loading ABI files:", e)
    exit()

# ✅ PancakeSwap Router contract address (Mainnet)
router_address = Web3.to_checksum_address("0x10ED43C718714eb63d5aA57B78B54704E256024E")
router = web3.eth.contract(address=router_address, abi=router_abi)

# ✅ Thresholds for whale detection (editable)
BNB_WHALE_THRESHOLD = 100  # 100+ BNB trades
TOKEN_TRANSFER_THRESHOLD = 1_000_000  # 1 million tokens

print("🔍 Monitoring BSC mempool for whale activity...")

def handle_transaction(tx_hash):
    try:
        tx = web3.eth.get_transaction(tx_hash)

        # Skip if contract creation or no recipient
        if tx['to'] is None:
            return

        tx_to = Web3.to_checksum_address(tx['to'])

        # Check PancakeSwap router transactions
        if tx_to == router_address:
            func_obj, params = router.decode_function_input(tx['input'])
            func_name = func_obj.fn_name

            if func_name in ['swapExactETHForTokens', 'swapExactTokensForETH', 'swapExactTokensForTokens']:
                value = web3.from_wei(tx['value'], 'ether')
                if float(value) >= BNB_WHALE_THRESHOLD:
                    print(f"🐋 WHALE TRADE DETECTED: {func_name}")
                    print(f"🔹 From: {tx['from']}")
                    print(f"🔹 Tx Hash: {tx_hash.hex()}")
                    print(f"💰 Value: {value:.4f} BNB\n")

        # Check for token transfers
        elif tx['input'].startswith("0xa9059cbb"):  # transfer(address,uint256)
            token_contract = web3.eth.contract(address=tx_to, abi=erc20_abi)
            decoded = token_contract.decode_function_input(tx['input'])
            _, params = decoded
            to_addr = params.get('_to') or params.get('recipient')
            amount = params.get('_value') or params.get('amount')

            decimals = token_contract.functions.decimals().call()
            symbol = token_contract.functions.symbol().call()
            human_amount = int(amount) / (10 ** decimals)

            if human_amount >= TOKEN_TRANSFER_THRESHOLD:
                print("🐋 WHALE TOKEN TRANSFER DETECTED")
                print(f"🔹 Token: {symbol}")
                print(f"🔹 From: {tx['from']}")
                print(f"🔹 To: {to_addr}")
                print(f"🔹 Amount: {human_amount:.2f} {symbol}")
                print(f"🔹 Tx Hash: {tx_hash.hex()}\n")

    except Exception:
        pass  # Silent fail to reduce noise; can log for debugging

# Main monitoring loop
seen_hashes = set()

while True:
    try:
        pending_block = web3.eth.get_block('pending', full_transactions=True)
        for tx in pending_block.transactions:
            if tx.hash not in seen_hashes:
                seen_hashes.add(tx.hash)
                handle_transaction(tx.hash)
        time.sleep(2)
    except KeyboardInterrupt:
        print("🛑 Stopped by user.")
        break
    except Exception as e:
        print("⚠️ Error:", e)
        time.sleep(5)

Crptoshield complete suit 
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

    Main.py
    import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'HONEY TRACKER'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'RUG PULL TRACKER'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'LIQUIDITY TRACKER'))

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

    GPT LLM MODEL
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


    
