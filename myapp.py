import streamlit as st
import requests
import pandas as pd

# Configuration de l'API
API_KEY = "7411eced-dc83-4346-8161-6b73528c432c"
API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

# Fonction pour récupérer les données des cryptos
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
                "percent_change_7d": data["data"][symbol]["quote"]["USD"]["percent_change_7d"],
                "volume_24h": data["data"][symbol]["quote"]["USD"]["volume_24h"],
            }
            for symbol in symbols
        }
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        return None

# Interface Streamlit
st.title("Tableau des Cryptomonnaies : Prix, Volume et Variations")
st.write("Données actualisées automatiquement.")

# Cryptomonnaies disponibles
selected_cryptos = ["BTC", "ETH", "SOL", "LUNA"]

# Récupération des données
crypto_data = get_crypto_data(selected_cryptos)

if crypto_data:
    # Préparation des données pour le tableau
    data = []
    for symbol, info in crypto_data.items():
        price = f"${info['price']:,.2f}"
        volume_24h = f"${info['volume_24h']:,.2f}"

        # Mise en couleur des variations
        percent_change_24h = info["percent_change_24h"]
        color_24h = "green" if percent_change_24h > 0 else "red"
        percent_change_24h_colored = f"<span style='color:{color_24h}'>{percent_change_24h:+.2f}%</span>"

        percent_change_7d = info["percent_change_7d"]
        color_7d = "green" if percent_change_7d > 0 else "red"
        percent_change_7d_colored = f"<span style='color:{color_7d}'>{percent_change_7d:+.2f}%</span>"

        # Ajouter les données dans une liste
        data.append([symbol, price, volume_24h, percent_change_24h_colored, percent_change_7d_colored])

    # Création du DataFrame
    df = pd.DataFrame(
        data,
        columns=["Cryptomonnaie", "Prix (USD)", "Volume (24h)", "Variation (24h)", "Variation (7j)"],
    )

    # Affichage des données avec mise en forme
    st.write(
        df.to_html(escape=False, index=False),
        unsafe_allow_html=True,
    )
