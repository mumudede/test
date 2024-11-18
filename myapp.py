import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime

# Configuration de l'API
API_KEY = "7411eced-dc83-4346-8161-6b73528c432c"
API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
HISTORY_FILE = "crypto_history.csv"

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

# Fonction pour sauvegarder les données dans un fichier CSV
def save_to_history(data):
    today = datetime.now().strftime("%d/%m/%y")  # Format DD/MM/YY
    records = []
    for symbol, info in data.items():
        records.append({
            "Date": today,
            "Cryptomonnaie": symbol,
            "Prix (USD)": info["price"],
            "Volume (24h)": info["volume_24h"],
            "Variation (24h)": info["percent_change_24h"],
            "Variation (7j)": info["percent_change_7d"],
        })
    new_df = pd.DataFrame(records)

    if os.path.exists(HISTORY_FILE):
        existing_data = pd.read_csv(HISTORY_FILE)

        # Vérifier si les données pour aujourd'hui existent déjà
        if today in existing_data["Date"].values:
            st.warning("Les données pour aujourd'hui ont déjà été historisées.")
            return

        # Combiner les nouvelles données avec les anciennes
        combined_df = pd.concat([existing_data, new_df], ignore_index=True)

        # Supprimer les doublons basés sur Date et Cryptomonnaie
        combined_df.drop_duplicates(subset=["Date", "Cryptomonnaie"], keep="last", inplace=True)
    else:
        combined_df = new_df

    combined_df.to_csv(HISTORY_FILE, index=False)
    st.success("Les données ont été historisées avec succès.")

# Fonction pour charger l'historique
def load_history():
    if os.path.exists(HISTORY_FILE):
        return pd.read_csv(HISTORY_FILE)
    else:
        return pd.DataFrame()

# Interface Streamlit
today = datetime.now().strftime("%d/%m/%y")  # Format DD/MM/YY
st.title(f"Tableau des Cryptomonnaies : {today}")

# Initialisation des données actuelles dans session_state
if "current_data" not in st.session_state:
    st.session_state["current_data"] = None

# Cryptomonnaies disponibles
selected_cryptos = ["BTC", "ETH", "SOL", "LUNA"]

# Gestion des boutons
if st.button("Actualiser"):
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
        st.session_state["current_data"] = pd.DataFrame(
            data,
            columns=["Cryptomonnaie", "Prix (USD)", "Volume (24h)", "Variation (24h)", "Variation (7j)"],
        )

if st.session_state["current_data"] is not None:
    # Affichage des données actuelles avec mise en forme
    st.subheader("Données actuelles")
    st.write(
        st.session_state["current_data"].to_html(escape=False, index=False),
        unsafe_allow_html=True,
    )

if st.button("Historiser"):
    if st.session_state["current_data"] is not None:
        crypto_data = get_crypto_data(selected_cryptos)
        save_to_history(crypto_data)
    else:
        st.warning("Veuillez actualiser les données avant de les historiser.")

# Affichage de l'historique
st.subheader("Historique des données")
history = load_history()

if not history.empty:
    # Application des règles d'affichage au tableau historique
    formatted_history = history.copy()
    formatted_history["Prix (USD)"] = formatted_history["Prix (USD)"].apply(lambda x: f"${x:,.2f}")
    formatted_history["Volume (24h)"] = formatted_history["Volume (24h)"].apply(lambda x: f"${x:,.2f}")
    formatted_history["Variation (24h)"] = formatted_history["Variation (24h)"].apply(
        lambda x: f"<span style='color:green'>{x:+.2f}%</span>" if x > 0 else f"<span style='color:red'>{x:+.2f}%</span>"
    )
    formatted_history["Variation (7j)"] = formatted_history["Variation (7j)"].apply(
        lambda x: f"<span style='color:green'>{x:+.2f}%</span>" if x > 0 else f"<span style='color:red'>{x:+.2f}%</span>"
    )
    st.write(
        formatted_history.to_html(escape=False, index=False),
        unsafe_allow_html=True,
    )
else:
    st.write("Aucun historique disponible.")
