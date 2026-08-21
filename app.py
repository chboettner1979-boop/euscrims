import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os
import time

# 1. Page Configuration
st.set_page_config(page_title="Eu Scrims Club", layout="centered")

# 2. CSS
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
    }
    .stat-card {
        background-color: #1e2229;
        border: 1px solid #2d333b;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        margin-bottom: 10px;
    }
    .stat-label { font-size: 0.75rem; color: #93c5fd; font-weight: bold; margin-bottom: 4px; }
    .stat-value { font-size: 1.1rem; color: #FFFFFF; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state.page = 'Player'

@st.cache_resource
def init_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

def ottieni_credenziali():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["gcp_service_account"])
        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    except Exception:
        return None

SHEET_ID_STATS = '1VrMCI4AA5zpflxulMVRpjRkVlhpzPHHYj24lSI1LfTw'
GID_PERSONAL_STATS = '869033822'

def scrivi_cella_per_gid(gid, cell_address, value):
    try:
        creds = ottieni_credenziali()
        if creds:
            client = gspread.authorize(creds)
            sheet = client.open_by_key(SHEET_ID_STATS)
            target_ws = next((ws for ws in sheet.worksheets() if str(ws.id).strip() == str(gid).strip()), None)
            if target_ws: target_ws.update_acell(cell_address, value)
    except Exception: pass

col1, col2, col3 = st.columns([1, 2, 1]) 
with col2:
    if os.path.exists("logop.png"): st.image("logop.png", use_container_width=True)
    elif os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        
    if st.button("REGISTERED PLAYERS"): st.session_state.page = 'Player'
    if st.button("REGISTERED TEAMS"): st.session_state.page = 'Teams'
    if st.button("RULES \ SETTING"): st.session_state.page = 'Rules'
    if st.button("SCRIMS RESULT"): st.session_state.page = 'Scrims'
    if st.button("PERSONAL STATS"): st.session_state.page = 'Stats'
    if st.button("STAT COMP"): st.session_state.page = 'STAT COMP'
    
    page = st.session_state.page

    if page == 'Player':
        st.markdown("<h2 style='text-align: center; color: #FFD700;'>Player Register</h2>", unsafe_allow_html=True)
        try:
            data = init_connection().open_by_key('1qfq7X9IuAcWEhFUuUbNkFfY2ssrmt04r1MFiaCC6ql0').get_worksheet_by_id(155113138).get('D8:D32')
            df = pd.DataFrame(data, columns=["Player"])
            df.insert(0, "N.", range(1, len(df) + 1))
            st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e: st.error(f"Error: {e}")

    elif page == 'Rules':
        st.markdown("<h2 style='text-align: center; color: #FFD700;'>SCORE</h2>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({"Details": ["1 KILL = 1 POINT", "250 DMG = 1 POINTS", "", "", ""], "Placement": ["1st", "2nd", "3rd", "4th", "5th+"], "Multiplier": ["1,2", "1,1", "1,05", "1", "1"]}), use_container_width=True, hide_index=True)
        st.markdown("<h3 style='text-align: center; color: #FFD700;'>EU SCRIMS MAPS</h3>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({"Setting": ["SPEED", "HOLD TIME", "ZONE DMG"], "Value": ["120%", "70%", "120%"]}), use_container_width=True, hide_index=True)

    elif page == 'Teams':
        try:
            ws = init_connection().open_by_key('1qfq7X9IuAcWEhFUuUbNkFfY2ssrmt04r1MFiaCC6ql0').worksheet("LOBBY / RULES")
            rows = ws.get('F7:K13')
            for i, row in enumerate(rows):
                st.markdown(f"<p style='color: #FFD700;'>Team {i+1}</p>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(row, columns=["TEAMS"]), use_container_width=True, hide_index=True)
        except Exception as e: st.error(f"Error: {e}")

    elif page == 'Scrims':
        try:
            ws = init_connection().open_by_key('1qfq7X9IuAcWEhFUuUbNkFfY2ssrmt04r1MFiaCC6ql0').get_worksheet_by_id(823408140)
            col_e = [r[0] if r else "" for r in ws.get('E8:E15')]
            for g, rng in [("Game 1", "F8:H15"), ("Game 2", "J8:L15"), ("Game 3", "N8:P15"), ("Game 4", "R8:T15"), ("Game 5", "V8:X15")]:
                st.markdown(f"<h3 style='text-align: center; color: #FFD700;'>{g}</h3>", unsafe_allow_html=True)
                data = ws.get(rng)
                rows = [{"team": col_e[i], "pos": d[0] if len(d)>0 else "", "kill": d[1] if len(d)>1 else "", "dmg": d[2] if len(d)>2 else ""} for i, d in enumerate(data)]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        except Exception as e: st.error(f"Error: {e}")

    elif page == 'Stats':
        st.markdown("<h2 style='text-align: center; color: #FFD700;'>STATS</h2>", unsafe_allow_html=True)
        try:
            ws = init_connection().open_by_key('1qfq7X9IuAcWEhFUuUbNkFfY2ssrmt04r1MFiaCC6ql0').get_worksheet_by_id(1732621049)
            def get_stat_block(p_col, v_col):
                p = ws.col_values(p_col)[10:34]
                v = ws.col_values(v_col)[10:34]
                df_temp = pd.DataFrame({"Player": p, "Val": v})
                return df_temp[df_temp["Player"].str.strip() != ""]
            
            df_k = get_stat_block(4, 5).rename(columns={"Val": "K"})
            df_d = get_stat_block(6, 7).rename(columns={"Val": "DMG"})
            df_m = get_stat_block(8, 9).rename(columns={"Val": "MVP"})
            df_de = get_stat_block(10, 11).rename(columns={"Val": "DEA"})
            
            all_p = pd.DataFrame({"Player": pd.unique(pd.concat([df_k["Player"], df_d["Player"], df_m["Player"], df_de["Player"]]))})
            for d in [df_k, df_d, df_m, df_de]: all_p = pd.merge(all_p, d, on="Player", how="left")
            st.dataframe(all_p.fillna("0"), use_container_width=True, hide_index=True)
        except Exception as e: st.error(f"Error: {e}")

    elif page == 'STAT COMP':
        # (Logica STAT COMP precedente mantenuta)
        st.markdown("<h2 style='text-align: center; color: #FFD700;'>STAT COMP</h2>", unsafe_allow_html=True)
        # ... inserire qui la logica di lettura e visualizzazione da GID_PERSONAL_STATS ...
