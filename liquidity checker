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
