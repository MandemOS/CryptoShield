# CryptoShield

CryptoShield is a comprehensive crypto token safety scanner with bots for honeypot detection, rug pull checking, liquidity analysis, and LP lock verification. It provides an API to scan tokens and deliver a risk score and verdict.

---

## Features

- Honeypot detection bot
- Rug pull checker bot
- Liquidity tracker bot
- LP lock checker
- FastAPI backend with REST API endpoints
- Chainstack integration for blockchain access

---

## Folder Structure

/CryptoShield
│
├── /honeypot_detector # Honeypot bot code
├── /rug_pull_checker # Rug pull bot code
├── /liquid # Liquidity tracker bot code
├── /lp # LP lock checker bot code
├── cryptoshield_api.py # Main FastAPI backend server
├── cryptoshield_requirements.txt # Python dependencies
├── .env.example # Example environment variables file
├── LICENSE
└── README.md # This file    
