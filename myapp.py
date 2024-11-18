import streamlit as st
import requests
import pandas as pd

# Configuration de l'API
API_KEY = "7411eced-dc83-4346-8161-6b73528c432c"
API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

# Fonction pour récupérer les prix et variations des cryptos
def get_crypto_data(symbols):
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
        return {
            symbol: {
                "price": data["data"][symbol]["quote"]["USD"]["price"],
                "percent_change_24h": data["data"][symbol]["quote"]["USD"]["percent_change_24h"],
            }
            for symbol in symbols
        }
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        return None

# Interface Streamlit
st.title("Prix et Variation des Cryptomonnaies")

# Cryptomonnaies disponibles
selected_cryptos = ["BTC", "ETH", "SOL", "LUNA"]

if st.button("Récupérer les prix et variations"):
    st.write("Récupération des données...")
    crypto_data = get_crypto_data(selected_cryptos)
    if crypto_data:
        # Préparation des données pour le tableau
        data = []
        for symbol, info in crypto_data.items():
            price = f"${info['price']:,.2f}"
            percent_change_24h = info["percent_change_24h"]
            # Couleur en fonction de la variation
            color = "green" if percent_change_24h > 0 else "red"
            percent_change_colored = f"<span style='color:{color}'>{percent_change_24h:+.2f}%</span>"
            data.append([symbol, price, percent_change_colored])

        # Création du DataFrame
        df = pd.DataFrame(data, columns=["Cryptomonnaie", "Prix (USD)", "Variation (24h)"])

        # Affichage des données avec mise en forme
        st.subheader("Prix et variations sur 24h des cryptomonnaies")
        st.write(
            df.to_html(escape=False, index=False),
            unsafe_allow_html=True,
        )
