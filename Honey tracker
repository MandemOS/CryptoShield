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
