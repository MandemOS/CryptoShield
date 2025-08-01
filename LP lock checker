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
