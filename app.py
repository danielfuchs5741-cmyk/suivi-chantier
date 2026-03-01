import streamlit as st
import pandas as pd
from io import BytesIO

# Configuration de la page
st.set_page_config(page_title="Gestionnaire de Chantier", layout="wide")

st.title("🏗️ Suivi Hebdomadaire des Ouvriers")

# 1. Saisie des données (Interface simplifiée)
with st.expander("➕ Ajouter une ligne de travail"):
    col1, col2, col3 = st.columns(3)
    with col1:
        ouvrier = st.selectbox("Ouvrier", ["Alice", "Bob", "Charlie"])
        date = st.date_input("Date")
    with col2:
        debut = st.time_input("Heure Début")
        fin = st.time_input("Heure Fin")
    with col3:
        tache = st.text_input("Tâche (ex: Maçonnerie)")
        vehicule = st.text_input("Véhicule (ex: Camion-01)")

# Données simulées pour l'exemple (à remplacer par une base de données plus tard)
data = {
    'Ouvrier': ['Alice', 'Alice', 'Bob', 'Alice', 'Bob', 'Alice'],
    'Date': ['2024-03-01', '2024-03-02', '2024-03-01', '2024-03-03', '2024-03-02', '2024-03-04'],
    'Debut': ['08:00', '08:00', '08:30', '08:00', '08:00', '07:00'],
    'Fin': ['17:30', '18:00', '17:00', '19:00', '17:30', '20:00'],
    'Pause_Min': [60, 60, 45, 30, 60, 30],
    'Taches': ['Terrassement', 'Maçonnerie', 'Livraison', 'Finition', 'Livraison', 'Dalle'],
    'Vehicule': ['Camion-01', 'Camion-01', 'Fourgon-B', 'Berline-02', 'Fourgon-B', 'Camion-01']
}

df = pd.DataFrame(data)
df['Date'] = pd.to_datetime(df['Date'])

# 2. Calculs (Logique identique à ton script)
df['TS_Debut'] = pd.to_datetime(df['Date'].dt.strftime('%Y-%m-%d') + ' ' + df['Debut'])
df['TS_Fin'] = pd.to_datetime(df['Date'].dt.strftime('%Y-%m-%d') + ' ' + df['Fin'])
df['Heures_Nettes'] = ((df['TS_Fin'] - df['TS_Debut']).dt.total_seconds() / 3600) - (df['Pause_Min'] / 60)
df['Semaine'] = df['Date'].dt.isocalendar().week

SEUIL_HS = 35.0
rapport = df.groupby(['Ouvrier', 'Semaine']).agg({
    'Heures_Nettes': 'sum',
    'Taches': lambda x: ', '.join(sorted(set(x))),
    'Vehicule': lambda x: ', '.join(sorted(set(x)))
}).reset_index()

rapport['HS'] = rapport['Heures_Nettes'].apply(lambda x: max(0, round(x - SEUIL_HS, 2)))
rapport['Heures_Nettes'] = rapport['Heures_Nettes'].round(2)

# 3. Affichage Web
st.subheader("📊 Rapport de la Semaine")

def color_hours(val):
    color = 'red' if val > SEUIL_HS else 'white'
    return f'color: {color}'

st.dataframe(rapport.style.applymap(color_hours, subset=['Heures_Nettes']))

# 4. Export Excel pour Mobile
output = BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    rapport.to_excel(writer, index=False, sheet_name='Rapport')
    writer.close()

st.download_button(
    label="📥 Télécharger le Rapport Excel",
    data=output.getvalue(),
    file_name="Rapport_Chantier.xlsx",
    mime="application/vnd.ms-excel"
)
