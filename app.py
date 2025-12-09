import datetime as dt
import time

import requests
import pandas as pd
import streamlit as st

# ----------------- CONFIG -----------------

COINS = {
    "Bitcoin (BTC)": "bitcoin",
    "Ethereum (ETH)": "ethereum",
    "Solana (SOL)": "solana",
    "Tether (USDT)": "tether",
    "BNB (BNB)": "binancecoin",
    "XRP (XRP)": "ripple",
}

FIAT_CURRENCY = "usd"
API_URL = "https://api.coingecko.com/api/v3/simple/price"


# ----------------- HELPER FUNCTIONS -----------------

def fetch_live_prices(selected_coin_ids):
    """
    Fetch live crypto prices & 24h change from CoinGecko API.
    """
    if not selected_coin_ids:
        return {}

    params = {
        "ids": ",".join(selected_coin_ids),
        "vs_currencies": FIAT_CURRENCY,
        "include_24hr_change": "true",
    }

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        raw = response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error calling CoinGecko API: {e}")
        return {}

    cleaned = {}
    for coin_id, info in raw.items():
        price = info.get(FIAT_CURRENCY)
        change = info.get(f"{FIAT_CURRENCY}_24h_change", 0.0)
        if price is None:
            continue
        cleaned[coin_id] = {
            "price": float(price),
            "change_24h": float(change),
        }

    return cleaned


def classify_risk(change_24h: float) -> str:
    """
    Classify risk level based on 24h percent change.
    """
    abs_change = abs(change_24h)
    if abs_change >= 10:
        return "HIGH"
    elif abs_change >= 5:
        return "MEDIUM"
    return "LOW"


def update_history(live_data):
    """
    Store history in session state.
    """
    if "history" not in st.session_state:
        st.session_state["history"] = pd.DataFrame(
            columns=["timestamp", "coin_name", "coin_id", "price", "change_24h", "risk"]
        )

    now = dt.datetime.utcnow()
    new_rows = []

    id_to_display = {v: k for k, v in COINS.items()}

    for coin_id, info in live_data.items():
        display_name = id_to_display.get(coin_id, coin_id)
        risk = classify_risk(info["change_24h"])

        new_rows.append(
            {
                "timestamp": now,
                "coin_name": display_name,
                "coin_id": coin_id,
                "price": info["price"],
                "change_24h": info["change_24h"],
                "risk": risk,
            }
        )

    if new_rows:
        df_new = pd.DataFrame(new_rows)
        st.session_state["history"] = pd.concat(
            [st.session_state["history"], df_new], ignore_index=True
        )


def get_latest_snapshot_df(live_data):
    """
    Convert latest live data into a display-friendly DataFrame.
    """
    rows = []
    id_to_display = {v: k for k, v in COINS.items()}

    for coin_id, info in live_data.items():
        display_name = id_to_display.get(coin_id, coin_id)

        rows.append(
            {
                "Coin": display_name,
                "Price (USD)": round(info["price"], 4),
                "24h Change (%)": round(info["change_24h"], 2),
                "Risk Level": classify_risk(info["change_24h"]),
            }
        )

    if not rows:
        return pd.DataFrame(columns=["Coin", "Price (USD)", "24h Change (%)", "Risk Level"])

    return pd.DataFrame(rows)


# ----------------- STREAMLIT APP -----------------

def main():
    st.set_page_config(
        page_title="Real-Time Crypto Risk Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("📈 Real-Time Crypto Risk & Price Dashboard")
    st.caption("Live crypto prices with risk analysis (using the CoinGecko API).")

    # Sidebar: Coin selection
    st.sidebar.header("Controls")

    selected_coins_display = st.sidebar.multiselect(
        "Select coins:",
        list(COINS.keys()),
        default=["Bitcoin (BTC)", "Ethereum (ETH)", "Solana (SOL)"],
    )

    # Sidebar note
    st.sidebar.info(
        "ℹ️ Click **'Fetch latest data'** to update prices.\n\n"
        "Click it multiple times to build real-time price history."
    )

    selected_ids = [COINS[name] for name in selected_coins_display]

    # Button to fetch new data
    if st.sidebar.button("🔄 Fetch latest data"):
        live_data = fetch_live_prices(selected_ids)

        if live_data:
            update_history(live_data)
            st.session_state["last_live_data"] = live_data
            st.success("✅ Data refreshed successfully!")
            time.sleep(0.3)

    if "last_live_data" not in st.session_state:
        st.session_state["last_live_data"] = {}

    if "history" not in st.session_state:
        st.session_state["history"] = pd.DataFrame(
            columns=["timestamp", "coin_name", "coin_id", "price", "change_24h", "risk"]
        )

    live_data = st.session_state["last_live_data"]
    history_df = st.session_state["history"]

    # ===================== CURRENT SNAPSHOT =====================
    st.subheader("Current Market Snapshot")

    if not live_data:
        st.warning("No live data yet. Select coins and click **Fetch latest data**.")
    else:
        snapshot_df = get_latest_snapshot_df(live_data)

        cols = st.columns(len(snapshot_df) or 1)
        for col, (_, row) in zip(cols, snapshot_df.iterrows()):
            with col:
                st.markdown(f"### {row['Coin']}")
                st.metric(
                    label="Price (USD)",
                    value=row["Price (USD)"],
                    delta=f"{row['24h Change (%)']}%",
                )

                risk = row["Risk Level"]
                if risk == "HIGH":
                    st.error(f"Risk: {risk}")
                elif risk == "MEDIUM":
                    st.warning(f"Risk: {risk}")
                else:
                    st.success(f"Risk: {risk}")

        st.divider()

    # ===================== PRICE HISTORY CHART =====================
    st.subheader("Price History (Current Session)")

    if history_df.empty:
        st.info("History will appear after fetching data multiple times.")
    else:
        filtered = history_df[
            history_df["coin_name"].isin(selected_coins_display)
        ]

        if filtered.empty:
            st.info("No history found for selected coins.")
        else:
            chart_df = filtered.pivot_table(
                index="timestamp",
                columns="coin_name",
                values="price",
                aggfunc="last",
            ).sort_index()

            st.line_chart(chart_df)

    # ===================== RAW DATA TABLE =====================
    st.subheader("Raw Data Table")

    if history_df.empty:
        st.info("No data collected yet.")
    else:
        st.dataframe(
            history_df.sort_values("timestamp", ascending=False).head(100),
            use_container_width=True,
        )

    # ===================== EXPLANATION SECTION =====================
    with st.expander("📘 How this Project Works"):
        st.markdown(
            """
            ### 🔍 Data Pipeline
            1. User selects crypto coins.
            2. App fetches live prices from the CoinGecko API.
            3. Data is cleaned and stored in session memory.
            4. A risk score (Low/Medium/High) is calculated from 24h change.
            5. Prices are visualized using real-time charts.

            ### 🎯 Why This Is a Data Science Project
            - External real-time API integration  
            - Data cleaning & feature engineering  
            - Risk classification logic  
            - Time-series visualization  
            - Interactive dashboard  
            """
        )


if __name__ == "__main__":
    main()
