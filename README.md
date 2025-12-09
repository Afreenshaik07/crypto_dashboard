# 📈 Real-Time Crypto Risk & Price Dashboard  
A fully interactive **real-time cryptocurrency analytics dashboard** built using **Python, Streamlit, Pandas, and the CoinGecko API**.  
The dashboard displays live crypto prices, calculates volatility-based risk scores, and visualizes price movements using beautiful charts.

---

# 🌟 Project Highlights

### 🔹 **Real-Time Price Fetching**
Fetches live cryptocurrency prices for popular coins such as:
- Bitcoin (BTC)
- Ethereum (ETH)
- Solana (SOL)
- BNB
- XRP  
…and more.

### 🔹 **Risk Classification Engine**
Based on 24-hour price change:
| 24h Change | Risk Level |
|-----------|------------|
| ≥ 10%     | 🔥 HIGH |
| 5%–10%    | ⚠️ MEDIUM |
| < 5%      | ✅ LOW |

### 🔹 **Interactive Dashboard**
- Multi-coin selection  
- Real-time metrics  
- Session-based history tracking  
- Line chart of price trends  
- Raw data viewer  

### 🔹 **Completely Free API**
Uses **CoinGecko public API** (no API key required).

---

# 🧰 Tech Stack

| Layer | Technology |
|-------|------------|
| UI Dashboard | Streamlit |
| Programming | Python |
| Data Handling | Pandas |
| API | CoinGecko Public API |
| Environment | venv |

---
# 📁 Project Structure
crypto_dashboard/
│── app.py # Main Streamlit application
│── requirements.txt # Required libraries
│── README.md # Project documentation
│── .gitignore # Ignore venv, pycache, etc.
└── venv/ # Virtual environment (ignored in GitHub)


