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
