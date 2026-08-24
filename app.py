import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os
import time

# 1. Page Configuration
st.set_page_config(page_title="Eu Scrims Club", layout="centered")

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
    
    .stat-card {
        background-color: #1e2229;
        border: 1px solid #2d333b;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        margin-bottom: 10px;
    }
    .stat-label {
        font-size: 0.75rem;
        color: #93c5fd;
        font-weight: bold;
        margin-bottom: 4px;
    }
    .stat-value {
        font-size: 1.1rem;
        color: #FFFFFF;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Page state management
if 'page' not in st.session_state:
    st.session_state.page = 'Player'

# Init Connection General
@st.cache_resource
def init_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

# Helper function per le credenziali (usato da STAT COMP)
def ottieni_credenziali():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["gcp_service_account"])
        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    except Exception:
        return None

# ID del foglio STAT COMP e GID specifico
SHEET_ID_STATS = '1VrMCI4AA5zpflxulMVRpjRkVlhpzPHHYj24lSI1LfTw'
GID_PERSONAL_STATS = '869033822'

def scrivi_cella_per_gid(gid, cell_address, value):
    try:
        creds = ottieni_credenziali()
        if creds:
            client = gspread.authorize(creds)
            sheet = client.open_by_key(SHEET_ID_STATS)
            target_ws = next((ws for ws in sheet.worksheets() if str(ws.id).strip() == str(gid).strip()), None)
            if target_ws:
                target_ws.update_acell(cell_address, value)
    except Exception:
        pass

# 3. Aligned Main Layout
col1, col2, col3 = st.columns([1, 2, 1]) 

with col2:
    if os.path.exists("logop.png"): st.image("logop.png", use_container_width=True)
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Pulsanti di navigazione completi
    if st.button("REGISTERED PLAYERS", use_container_width=True): st.session_state.page = 'Player'
    if st.button("REGISTERED TEAMS", use_container_width=True): st.session_state.page = 'Teams'
    if st.button("RULES \ SETTING", use_container_width=True): st.session_state.page = 'Rules'
    if st.button("SCRIMS RESULT", use_container_width=True): st.session_state.page = 'Scrims'
    if st.button("PERSONAL STATS", use_container_width=True): st.session_state.page = 'Stats'
    if st.button("STAT COMP", use_container_width=True): st.session_state.page = 'STAT COMP'
    
    page = st.session_state.page

    # DYNAMIC CONTENT
    if page == 'Rules':
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

    elif page == 'Teams':
        st.markdown("<h2 style='text-align: center; color: #FFD700;'>TEAMS</h2>", unsafe_allow_html=True)
        try:
            ws = init_connection().open_by_key('1qfq7X9IuAcWEhFUuUbNkFfY2ssrmt04r1MFiaCC6ql0').worksheet("LOBBY / RULES")
            rows = ws.get('F7:K13')
            for i, row in enumerate(rows):
                while len(row) < 6: row.append("")
                st.markdown(f"<p style='color: #FFD700; font-weight: bold;'>Team {i+1}</p>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(row, columns=["TEAMS"]), use_container_width=True, hide_index=True)
        except Exception as e: st.error(f"Error: {e}")

    elif page == 'Scrims':
        st.markdown("<h2 style='text-align: center; color: #FFD700;'>SCRIMS</h2>", unsafe_allow_html=True)
        try:
            ws = init_connection().open_by_key('1qfq7X9IuAcWEhFUuUbNkFfY2ssrmt04r1MFiaCC6ql0').get_worksheet_by_id(823408140)
            
            col_raw = ws.get('E8:E15')
            col_e = [r[0] if (r and len(r) > 0 and r[0] is not None) else "" for r in col_raw]
            while len(col_e) < 8: col_e.append("")
            
            for g, rng in [("Game 1", "F8:H15"), ("Game 2", "J8:L15"), ("Game 3", "N8:P15"), ("Game 4", "R8:T15"), ("Game 5", "V8:X15")]:
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
            
            st.markdown("<h3 style='text-align: center; color: #FFD700;'>Total Score</h3>", unsafe_allow_html=True)
            
            data_score = ws.get('AE8:AF15')
            teams = []
            points = []
            
            for i in range(8):
                if i < len(data_score):
                    row = data_score[i]
                    teams.append(row[0] if (len(row) > 0 and row[0] is not None) else "")
                    points.append(row[1] if (len(row) > 1 and row[1] is not None) else "")
                else:
                    teams.append("")
                    points.append("")
            
            df_score = pd.DataFrame({
                "Position": range(1, 9), 
                "Team": teams, 
                "Points": points
            })
            
            st.dataframe(df_score, use_container_width=True, hide_index=True)
            
        except Exception as e: 
            st.error(f"Error: {e}")

    elif page == 'Stats':
        st.markdown("<h2 style='text-align: center; color: #FFD700;'>STATS</h2>", unsafe_allow_html=True)
        try:
            ws = init_connection().open_by_key(SHEET_ID_STATS).get_worksheet_by_id(1732621049)
            raw_data = ws.get('D11:K35')
            
            player_data_dict = {}
            # ... (mantieni il codice di popolamento del dict che avevi prima) ...
            for r in raw_data:
                while len(r) < 8: r.append("")
                # (Logica di estrazione dei 4 blocchi D, F, H, J invariata)
                p_kill, val_kill = str(r[0]).strip(), str(r[1]).strip()
                if p_kill and p_kill.upper() not in ["NAN", "NONE", ""]:
                    if p_kill not in player_data_dict: player_data_dict[p_kill] = {"K": 0, "D": 0, "MVP": 0, "DEA": 0}
                    player_data_dict[p_kill]["K"] = val_kill if val_kill else 0
                
                p_dmg, val_dmg = str(r[2]).strip(), str(r[3]).strip()
                if p_dmg and p_dmg.upper() not in ["NAN", "NONE", ""]:
                    if p_dmg not in player_data_dict: player_data_dict[p_dmg] = {"K": 0, "D": 0, "MVP": 0, "DEA": 0}
                    player_data_dict[p_dmg]["D"] = val_dmg if val_dmg else 0

                p_mvp, val_mvp = str(r[4]).strip(), str(r[5]).strip()
                if p_mvp and p_mvp.upper() not in ["NAN", "NONE", ""]:
                    if p_mvp not in player_data_dict: player_data_dict[p_mvp] = {"K": 0, "D": 0, "MVP": 0, "DEA": 0}
                    player_data_dict[p_mvp]["MVP"] = val_mvp if val_mvp else 0

                p_dea, val_dea = str(r[6]).strip(), str(r[7]).strip()
                if p_dea and p_dea.upper() not in ["NAN", "NONE", ""]:
                    if p_dea not in player_data_dict: player_data_dict[p_dea] = {"K": 0, "D": 0, "MVP": 0, "DEA": 0}
                    player_data_dict[p_dea]["DEA"] = val_dea if val_dea else 0

            rows = [{"Player": k, **v} for k, v in player_data_dict.items()]
            df = pd.DataFrame(rows)
            
            # --- FIX ORDINAMENTO ---
            if not df.empty:
                # Forza le K a numero per ordinare correttamente
                df['K'] = pd.to_numeric(df['K'], errors='coerce').fillna(0)
                # Ordina per K decrescente
                df = df.sort_values(by="K", ascending=False).reset_index(drop=True)
            
            st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e: 
            st.error(f"Error: {e}")

    elif page == 'STAT COMP':
        st.markdown("<h2 style='text-align: center; color: #FFD700;'>STAT COMP</h2>", unsafe_allow_html=True)
        
        target_ws = None
        current_d13_val = ""
        extracted_players = []

        try:
            creds = ottieni_credenziali()
            if creds:
                client = gspread.authorize(creds)
                sheet = client.open_by_key(SHEET_ID_STATS)
                target_ws = next((ws for ws in sheet.worksheets() if str(ws.id).strip() == str(GID_PERSONAL_STATS).strip()), None)
                
                if target_ws:
                    d13_raw = target_ws.acell("D13").value
                    if d13_raw is not None and str(d13_raw).strip() != "":
                        current_d13_val = str(d13_raw).strip()
                    
                    col_c_values = target_ws.get("C12:C60")
                    for row in col_c_values:
                        if row and len(row) > 0:
                            p = str(row[0]).strip()
                            if p and p.lower() not in ["nan", "none", ""]:
                                extracted_players.append(p)
                    extracted_players = list(dict.fromkeys(extracted_players))
        except Exception as e:
            st.warning(f"Error reading initial Personal Stats sheet: {e}")

        if not extracted_players:
            extracted_players = ["No players available"]

        player_index = 0
        if current_d13_val in extracted_players:
            player_index = extracted_players.index(current_d13_val)

        selected_d13_val = st.selectbox("Select Player", extracted_players, index=player_index, key="sb_player_d13")
        
        if str(selected_d13_val).strip().lower() != str(current_d13_val).strip().lower():
            scrivi_cella_per_gid(GID_PERSONAL_STATS, "D13", selected_d13_val)
            st.rerun()

        with st.spinner("Updating data..."):
            time.sleep(0.2)

        st.markdown("---")

        def format_val(val, is_percentage=False, decimals=2):
            try:
                if val is None or str(val).strip() == "" or str(val).strip().lower() in ["nan", "none", "#n/a", "#valore!"]:
                    return "0.00%" if is_percentage else "0"
                clean_val = str(val).replace("%", "").strip().replace(",", ".")
                num = float(clean_val)
                factor = 10 ** decimals
                truncated = int(num * factor) / factor
                if is_percentage:
                    return f"{truncated:.{decimals}f}%"
                elif truncated.is_integer():
                    return str(int(truncated))
                else:
                    return f"{truncated:.{decimals}f}"
            except Exception:
                return str(val) if val is not None and str(val).strip() != "" else ("0.00%" if is_percentage else "0")

        summary_fired, summary_hit, summary_acc, summary_kill, summary_dmg, summary_mvp, summary_death = "0", "0", "0.00%", "0", "0", "0", "0"
        faster_banana_val = "-"
        deadliest_w, deadliest_d, deadliest_a = "-", "0", "0.00%"
        weapon_rows_data = []

        try:
            if target_ws:
                f16_l16 = target_ws.get("F16:L16")
                if f16_l16 and len(f16_l16) > 0:
                    row_vals = f16_l16[0]
                    summary_fired = format_val(row_vals[0] if len(row_vals) > 0 else 0)
                    summary_hit = format_val(row_vals[1] if len(row_vals) > 1 else 0)
                    summary_acc = format_val(row_vals[2] if len(row_vals) > 2 else 0, is_percentage=True)
                    summary_kill = format_val(row_vals[3] if len(row_vals) > 3 else 0)
                    summary_dmg = format_val(row_vals[4] if len(row_vals) > 4 else 0)
                    summary_mvp = format_val(row_vals[5] if len(row_vals) > 5 else 0)
                    summary_death = format_val(row_vals[6] if len(row_vals) > 6 else 0)

                j18_l18 = target_ws.get("J18:L18")
                if j18_l18 and len(j18_l18) > 0 and len(j18_l18[0]) > 0:
                    faster_banana_val = format_val(j18_l18[0][0])

                h20_l21 = target_ws.get("H20:L21")
                if h20_l21 and len(h20_l21) > 0:
                    raw_w = h20_l21[0][0] if len(h20_l21[0]) > 0 else "-"
                    deadliest_w = str(raw_w).strip() if raw_w and str(raw_w).strip().lower() not in ["nan", "none", ""] else "-"
                    
                    if len(h20_l21) > 1:
                        deadliest_d = format_val(h20_l21[1][3] if len(h20_l21[1]) > 3 else 0)
                        deadliest_a = format_val(h20_l21[1][4] if len(h20_l21[1]) > 4 else 0, is_percentage=True)

                weapons_raw = target_ws.get("F27:L68")
                if weapons_raw:
                    for r_data in weapons_raw:
                        if r_data and len(r_data) > 0:
                            w_name = str(r_data[0]).strip()
                            if w_name and w_name.upper() not in ["NAN", "NONE", ""]:
                                weapon_rows_data.append({
                                    "WEAPON": w_name,
                                    "TOT SHOTS": format_val(r_data[1] if len(r_data) > 1 else 0, is_percentage=False),
                                    "SHOT HIT": format_val(r_data[2] if len(r_data) > 2 else 0, is_percentage=False),
                                    "ACC%": format_val(r_data[3] if len(r_data) > 3 else 0, is_percentage=True),
                                    "DMG": format_val(r_data[4] if len(r_data) > 4 else 0, is_percentage=False),
                                    "HEADSHOT": format_val(r_data[5] if len(r_data) > 5 else 0, is_percentage=False),
                                    "MAX DISTANCE": format_val(r_data[6] if len(r_data) > 6 else 0, is_percentage=False)
                                })
        except Exception as e:
            st.warning(f"Error reading dashboard data: {e}")

        st.markdown("<h4 style='color: #93c5fd; font-size: 1rem;'>MATCH SUMMARY</h4>", unsafe_allow_html=True)
        c_grid1, c_grid2, c_grid3 = st.columns(3)
        
        with c_grid1:
            st.markdown(f"<div class='stat-card'><div class='stat-label'>FIRED</div><div class='stat-value'>{summary_fired}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='stat-card'><div class='stat-label'>ACCURACY</div><div class='stat-value'>{summary_acc}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='stat-card'><div class='stat-label'>DMG</div><div class='stat-value'>{summary_dmg}</div></div>", unsafe_allow_html=True)
        with c_grid2:
            st.markdown(f"<div class='stat-card'><div class='stat-label'>SHOT HIT</div><div class='stat-value'>{summary_hit}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='stat-card'><div class='stat-label'>KILL</div><div class='stat-value'>{summary_kill}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='stat-card'><div class='stat-label'>MVP</div><div class='stat-value'>{summary_mvp}</div></div>", unsafe_allow_html=True)
        with c_grid3:
            st.markdown(f"<div class='stat-card'><div class='stat-label'>DEATH</div><div class='stat-value'>{summary_death}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='stat-card'><div class='stat-label'>FASTER BANANA</div><div class='stat-value'>{faster_banana_val}</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("<h4 style='color: #93c5fd; font-size: 1rem;'>DEADLIEST WEAPON</h4>", unsafe_allow_html=True)
        dw_col1, dw_col2, dw_col3 = st.columns(3)
        with dw_col1:
            st.markdown(f"<div class='stat-card'><div class='stat-label'>WEAPON</div><div class='stat-value' style='font-size: 0.85rem;'>{deadliest_w}</div></div>", unsafe_allow_html=True)
        with dw_col2:
            st.markdown(f"<div class='stat-card'><div class='stat-label'>DMG</div><div class='stat-value'>{deadliest_d}</div></div>", unsafe_allow_html=True)
        with dw_col3:
            st.markdown(f"<div class='stat-card'><div class='stat-label'>ACC%</div><div class='stat-value'>{deadliest_a}</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("<h4 style='color: #93c5fd; text-align: center;'>WEAPON PERFORMANCE</h4>", unsafe_allow_html=True)
        
        if weapon_rows_data:
            df_weapons_final = pd.DataFrame(weapon_rows_data)
        else:
            df_weapons_final = pd.DataFrame(columns=["WEAPON", "TOT SHOTS", "SHOT HIT", "ACC%", "DMG", "HEADSHOT", "MAX DISTANCE"])

        st.dataframe(df_weapons_final, use_container_width=True, hide_index=True)

    else:
        st.markdown("<h2 style='text-align: center; color: #FFD700;'>Player Register</h2>", unsafe_allow_html=True)
        try:
            data = init_connection().open_by_key('1qfq7X9IuAcWEhFUuUbNkFfY2ssrmt04r1MFiaCC6ql0').get_worksheet_by_id(155113138).get('D8:D32')
            df = pd.DataFrame(data, columns=["Player"])
            df.insert(0, "N.", range(1, len(df) + 1))
            st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e: 
            st.error(f"Error: {e}")
