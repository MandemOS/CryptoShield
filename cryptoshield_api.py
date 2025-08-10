import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from web3 import Web3

# Load env vars from .env file
load_dotenv()
CHAINSTACK_URL = os.getenv("CHAINSTACK_ACCESS_KEY")

if not CHAINSTACK_URL:
    print("⚠️ Warning: CHAINSTACK_ACCESS_KEY not found in .env")
else:
    print(f"✅ Loaded Chainstack URL: {CHAINSTACK_URL}")

# Add your bot folders to sys.path for imports
BASE_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(BASE_DIR, "honey_tracker"))
sys.path.insert(0, os.path.join(BASE_DIR, "rug_pull_tracker"))
sys.path.insert(0, os.path.join(BASE_DIR, "liquid"))  # ← updated folder name
sys.path.insert(0, os.path.join(BASE_DIR, "lp"))

# Import your existing bot functions
from honeypot_detector import run_honeypot
from rug_pull_checker import run_rugpull
from liquidity_checker import run_liquidity  # ← updated import path
from lp_lock_checker import run_lp_lock_check

# PancakeSwap factory info for LP token lookup
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

app = FastAPI(title="CryptoShield API")

class ScanResult(BaseModel):
    honeypot: dict
    rugpull: dict
    liquidity: dict
    lp_lock: Optional[list]
    score: int
    verdict: str

@app.get("/")
async def root():
    return {"message": "Welcome to CryptoShield API. Use /scan/{token_address} to scan tokens."}

def get_lp_token_address(token_address: str, chainstack_url: str) -> Optional[str]:
    try:
        w3 = Web3(Web3.HTTPProvider(chainstack_url))
        factory = w3.eth.contract(address=Web3.to_checksum_address(PANCAKE_FACTORY_ADDRESS), abi=PANCAKE_FACTORY_ABI)
        lp_address = factory.functions.getPair(Web3.to_checksum_address(token_address), Web3.to_checksum_address(WBNB_ADDRESS)).call()
        if lp_address == "0x0000000000000000000000000000000000000000":
            return None
        return lp_address
    except Exception:
        return None

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

def get_verdict(score):
    if score >= 7:
        return "✅ PASSED — GOOD TO BUY"
    elif score >= 4:
        return "⚠️ WARNING — PROCEED WITH CAUTION"
    else:
        return "❌ FAILED — SCAM LIKELY"

@app.get("/scan/{token_address}", response_model=ScanResult)
def scan_token(token_address: str):
    # Basic validation
    if not token_address.startswith("0x") or len(token_address) != 42:
        raise HTTPException(status_code=400, detail="Invalid token address format")

    # Run scans
    try:
        honeypot_result = run_honeypot(token_address)
    except Exception as e:
        honeypot_result = {"error": str(e), "passed": False, "messages": [str(e)]}

    try:
        rugpull_result = run_rugpull(token_address)
    except Exception as e:
        rugpull_result = {"error": str(e), "messages": [str(e)]}

    try:
        liquidity_result = run_liquidity(token_address)
    except Exception as e:
        liquidity_result = {"error": str(e), "messages": [str(e)]}

    # LP lock check (optional, requires chainstack url)
    try:
        lp_token_address = get_lp_token_address(token_address, CHAINSTACK_URL) if CHAINSTACK_URL else None
        if lp_token_address is None:
            lp_lock_result = [{"locker": "LP Lock Check", "error": "No LP token pair found"}]
        else:
            lp_lock_result = run_lp_lock_check(lp_token_address, chainstack_url=CHAINSTACK_URL)
    except Exception as e:
        lp_lock_result = [{"locker": "LP Lock Check", "error": str(e)}]

    # Score & verdict
    score = calculate_score(honeypot_result, rugpull_result, liquidity_result)
    verdict = get_verdict(score)

    return ScanResult(
        honeypot=honeypot_result,
        rugpull=rugpull_result,
        liquidity=liquidity_result,
        lp_lock=lp_lock_result,
        score=score,
        verdict=verdict,
    )
