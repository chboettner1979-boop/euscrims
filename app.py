import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os

# 1. Page Configuration
st.set_page_config(page_title="Euro Scrims", layout="centered")

# 2. CSS for Dark Mode, buttons, and clean tables
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #FFFFFF; }
    
    div[data-testid="stDataFrame"] { background-color: #000000; width: 100% !important; }
    div[data-testid="stDataFrame"] div[data-baseweb="block"] { background-color: #000000 !important; }
    div[data-testid="stDataFrame"] table, tr, th, td {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-color: #FFFFFF !important;
        font-size: 11px !important;
    }

    .stButton button {
        background-color: #FFD700 !important;
        color: #00008B !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
        width: 100% !important;
        height: 40px !important;
        white-space: nowrap !important;
    }
    .stButton button:hover { background-color: #FFC000 !important; color: #0000FF !important; }
    </style>
    """, unsafe_allow_html=True)

# Page state management
if 'page' not in st.session_state:
    st.session_state.page = 'Player'

# Init Connection
@st.cache_resource
def init_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

# 3. Aligned Main Layout
col1, col2, col3 = st.columns([1, 2, 1]) 

with col2:
    if os.path.exists("logop.png"): st.image("logop.png", use_container_width=True)
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Pulsanti uno sopra l'altro
    if st.button("REGISTERED PLAYERS", use_container_width=True): st.session_state.page = 'Player'
    if st.button("REGISTERED TEAMS", use_container_width=True): st.session_state.page = 'Teams'
    if st.button("RULES \ SETTING", use_container_width=True): st.session_state.page = 'Rules'
    if st.button("SCRIMS RESULT", use_container_width=True): st.session_state.page = 'Scrims'
    if st.button("PERSONAL STATS", use_container_width=True): st.session_state.page = 'Stats'
    

    # DYNAMIC CONTENT
    if st.session_state.page == 'Rules':
        st.markdown("<h2 style='text-align: center; color: #FFD700;'>SCORE</h2>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            "Details": ["1 KILL = 1 POINT", "250 DMG = 1 POINTS", "", "", ""],
            "Placement": ["1st SCORE X", "2nd SCORE X", "3rd SCORE X", "4th SCORE X", "5th or low SCORE X"],
            "Multiplier": ["1,2", "1,1", "1,05", "1", "1"]
        }), use_container_width=True, hide_index=True)
        
        st.markdown("<br><h2 style='text-align: center; color: #FFD700;'>EU SCRIMS MAPS</h2>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({"Setting": ["SPEED", "HOLD TIME", "ZONE DEMAGE"], "Value": ["120%", "70%", "120%"]}), use_container_width=True, hide_index=True)
        st.markdown("<h3 style='text-align: center; color: #FFD700;'>GENERAL RULES</h3>", unsafe_allow_html=True)
        st.markdown("- **THE SCRIMS IS 5 MATCHES**\n- **FIRST GAME STARTS 5 MIN AFTER SCHEDULED TIME**\n- **LAST MINUTE SUBS GOES THROUGH ADMINS**\n- **USE THE SAME IGN**")

    elif st.session_state.page == 'Teams':
        st.markdown("<h2 style='text-align: center; color: #FFD700;'>TEAMS</h2>", unsafe_allow_html=True)
        try:
            ws = init_connection().open_by_key('1qfq7X9IuAcWEhFUuUbNkFfY2ssrmt04r1MFiaCC6ql0').worksheet("LOBBY / RULES")
            rows = ws.get('F7:K13')
            for i, row in enumerate(rows):
                while len(row) < 6: row.append("")
                st.markdown(f"<p style='color: #FFD700; font-weight: bold;'>Team {i+1}</p>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(row, columns=["TEAMS"]), use_container_width=True, hide_index=True)
        except Exception as e: st.error(f"Error: {e}")

    elif st.session_state.page == 'Scrims':
        st.markdown("<h2 style='text-align: center; color: #FFD700;'>SCRIMS</h2>", unsafe_allow_html=True)
        try:
            ws = init_connection().open_by_key('1qfq7X9IuAcWEhFUuUbNkFfY2ssrmt04r1MFiaCC6ql0').get_worksheet_by_id(823408140)
            
            # Legge correttamente i nomi dei team
            col_raw = ws.get('E8:E15')
            col_e = [r[0] if (r and len(r) > 0 and r[0] is not None) else "" for r in col_raw]
            while len(col_e) < 8: col_e.append("")
            
            for g, rng in [("Game 1", "F8:H15"), ("Game 2", "J8:L15"), ("Game 3", "N8:P15"), ("Game 4", "R8:T15"), ("Game 5", "V8:X15")]:
                # Titolo centrato aggiunto qui
                st.markdown(f"<h3 style='text-align: center; color: #FFD700;'>{g}</h3>", unsafe_allow_html=True)
                data = ws.get(rng)
                rows = []
                for idx in range(8):
                    r = data[idx] if idx < len(data) else []
                    rows.append({
                        "team": col_e[idx], 
                        "pos": r[0] if len(r)>0 else "", 
                        "kill": r[1] if len(r)>1 else "", 
                        "dmg": r[2] if len(r)>2 else ""
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            
            # Titolo Total Score centrato
        st.markdown("<h3 style='text-align: center; color: #FFD700;'>Total Score</h3>", unsafe_allow_html=True)
        
        try:
            # Leggiamo l'intero blocco AE8:AF15
            # ws.get restituirà una lista di liste, es: [['TeamA', 10], ['TeamB', 5], ...]
            data = ws.get('AE8:AF15')
            
            # Prepariamo le liste per le colonne
            teams = []
            points = []
            
            # Iteriamo per assicurarci di avere esattamente 8 righe
            for i in range(8):
                # Controlliamo se la riga esiste nei dati scaricati
                if i < len(data):
                    row = data[i]
                    # Recupera il nome team (colonna AE, indice 0)
                    teams.append(row[0] if (len(row) > 0 and row[0] is not None) else "")
                    # Recupera i punti (colonna AF, indice 1)
                    points.append(row[1] if (len(row) > 1 and row[1] is not None) else "")
                else:
                    # Se il foglio ha meno righe, riempiamo con vuoto
                    teams.append("")
                    points.append("")
            
            # Crea e visualizza il DataFrame
            df = pd.DataFrame({
                "Position": range(1, 9), 
                "Team": teams, 
                "Points": points
            })
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
        except Exception as e: 
            st.error(f"Errore nella lettura dei dati: {e}")

    elif st.session_state.page == 'Stats':
        st.markdown("<h2 style='text-align: center; color: #FFD700;'>STATS</h2>", unsafe_allow_html=True)
        try:
            ws = init_connection().open_by_key('1qfq7X9IuAcWEhFUuUbNkFfY2ssrmt04r1MFiaCC6ql0').get_worksheet_by_id(1732621049)
            
            # Funzione pulita senza alcun troncamento
            def fetch_full_col(rng):
                raw = ws.get(rng)
                col = []
                for r in raw:
                    val = str(r[0]) if (r and len(r) > 0 and r[0] is not None) else ""
                    col.append(val)
                while len(col) < 24:
                    col.append("")
                return col[:24]

            df = pd.DataFrame({
                "Player": fetch_full_col('D11:D34'), 
                "K": fetch_full_col('E11:E34'),       
                "D": fetch_full_col('G11:G34'),
                "MVP": fetch_full_col('I11:I34'),
                "DEA": fetch_full_col('K11:K34')
            })
            
            # Configuriamo solo la larghezza visiva delle colonne senza toccare i dati interni
            st.dataframe(
                df, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Player": st.column_config.TextColumn("Player", width="medium"),
                    "K": st.column_config.TextColumn("K", width="small"),
                    "D": st.column_config.TextColumn("D", width="small"),
                    "MVP": st.column_config.TextColumn("MVP", width="small"),
                    "DEA": st.column_config.TextColumn("DEA", width="small")
                }
            )
        except Exception as e: st.error(f"Error: {e}")

    else:
        st.markdown("<h2 style='text-align: center; color: #FFD700;'>Player Register</h2>", unsafe_allow_html=True)
        try:
            data = init_connection().open_by_key('1qfq7X9IuAcWEhFUuUbNkFfY2ssrmt04r1MFiaCC6ql0').get_worksheet_by_id(155113138).get('D8:D32')
            df = pd.DataFrame(data, columns=["Player"])
            df.insert(0, "N.", range(1, len(df) + 1))
            st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e: st.error(f"Error: {e}")
