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

        # Supprimer les données avec des dates au format YY-MM-DD
        existing_data = existing_data[~existing_data["Date"].str.match(r"^\d{4}-\d{2}-\d{2}$")]

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

# Fonction pour appliquer les règles de formatage aux colonnes
def format_history(df):
    def style_row(row):
        # Format du prix
        row["Prix (USD)"] = f"${row['Prix (USD)']:,.2f}"
        # Format du volume
        row["Volume (24h)"] = f"${row['Volume (24h)']:,.2f}"
        # Couleur des variations
        row["Variation (24h)"] = f"<span style='color:green'>{row['Variation (24h)']:+.2f}%</span>" if row["Variation (24h)"] > 0 else f"<span style='color:red'>{row['Variation (24h)']:+.2f}%</span>"
        row["Variation (7j)"] = f"<span style='color:green'>{row['Variation (7j)']:+.2f}%</span>" if row["Variation (7j)"] > 0 else f"<span style='color:red'>{row['Variation (7j)']:+.2f}%</span>"
        return row

    return df.apply(style_row, axis=1)

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
        st.session_state["current_data"] = prepare_current_data(crypto_data)

if st.session_state["current_data"] is not None:
    # Affichage des données actuelles avec mise en forme
    st.subheader("Données actuelles")
    st.write(
        st.session_state["current_data"].to_html(escape=False, index=False),
        unsafe_allow_html=True,
    )

if st.button("Historiser"):
    if st.session_state["current_data"] is not None:
        save_to_history(get_crypto_data(selected_cryptos))
    else:
        st.warning("Veuillez actualiser les données avant de les historiser.")

# Affichage de l'historique
st.subheader("Historique des données")
history = load_history()

if not history.empty:
    # Application des règles de formatage au tableau historique
    history = format_history(history)
    st.write(
        history.to_html(escape=False, index=False),
        unsafe_allow_html=True,
    )
else:
    st.write("Aucun historique disponible.")
