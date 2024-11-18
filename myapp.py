import streamlit as st
import requests

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

# Liste des cryptos à choisir
available_cryptos = [
    "BTC", "ETH", "BNB", "XRP", "SOL", "ADA", "DOGE", "DOT", "MATIC", "LTC",
    "SHIB", "AVAX", "UNI", "LINK", "ATOM"
]
selected_cryptos = st.sidebar.multiselect(
    "Choisissez jusqu'à 10 cryptomonnaies",
    available_cryptos,
    default=["BTC", "ETH", "BNB"]
)

if len(selected_cryptos) > 10:
    st.warning("Vous ne pouvez sélectionner que 10 cryptomonnaies au maximum.")
else:
    if st.sidebar.button("Récupérer les prix"):
        st.write("Récupération des données...")
        prices = get_crypto_prices(selected_cryptos)
        if prices:
            st.subheader("Prix actuels des cryptomonnaies (en USD)")
            for symbol, price in prices.items():
                st.write(f"**{symbol}** : ${price:,.2f}")
