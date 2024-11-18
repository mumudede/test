import streamlit as st
import requests
import pandas as pd

# Configuration de l'API
API_KEY = "7411eced-dc83-4346-8161-6b73528c432c"
API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

# Fonction pour récupérer les prix des cryptos
def get_crypto_prices(symbols):
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": API_KEY,
    }
    params = {
        "symbol": ",".join(symbols),
        "convert": "USD",
    }
    try:
        response = requests.get(API_URL, headers=headers, params=params)
        data = response.json()
        return {symbol: data["data"][symbol]["quote"]["USD"]["price"] for symbol in symbols}
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        return None

# Interface Streamlit
st.title("Prix en Direct des Cryptomonnaies")
st.sidebar.header("Configurer l'application")

# Liste des cryptomonnaies disponibles
available_cryptos = [
    "BTC", "ETH", "BNB", "XRP", "SOL", "ADA", "DOGE", "DOT", "MATIC", "LTC",
    "SHIB", "AVAX", "UNI", "LINK", "ATOM"
]

# Affichage des cases à cocher pour les cryptos
st.sidebar.subheader("Sélectionnez jusqu'à 10 cryptomonnaies")
selected_cryptos = []
for crypto in available_cryptos:
    if st.sidebar.checkbox(crypto, value=False):
        selected_cryptos.append(crypto)

# Limite de sélection
if len(selected_cryptos) > 10:
    st.warning("Vous ne pouvez sélectionner que 10 cryptomonnaies au maximum.")
else:
    if st.sidebar.button("Récupérer les prix"):
        st.write("Récupération des données...")
        prices = get_crypto_prices(selected_cryptos)
        if prices:
            # Conversion des données en tableau
            df = pd.DataFrame(
                {
                    "Cryptomonnaie": list(prices.keys()),
                    "Prix (USD)": [f"${price:,.2f}" for price in prices.values()],
                }
            )
            st.subheader("Prix actuels des cryptomonnaies")
            st.table(df)
