import streamlit as st
import pandas as pd
import time
import gspread

# 1. Page Configuration
st.set_page_config(page_title="EuroCup Dashboard", layout="centered")

# --- CONFIGURAZIONE GOOGLE SHEETS & CREDENZIALI ---
SHEET_ID = '148tcAz14DpqYQV0ug5I1LmQuZ3AFrS0ebtl2-WPUIUY'
GID_PERSONAL_STATS = '327527248' # Sostituisci con il GID corretto della scheda Personal Stats se diverso

# Nuova costante per la pagina Stat Comp
SHEET_ID_COMP = '1VrMCI4AA5zpflxulMVRpjRkVlhpzPHHYj24lSI1LfTw'
GID_STAT_COMP = '869033822'

def ottieni_credenziali():
    """Recupera le credenziali da st.secrets per gspread"""
    try:
        if "gcp_service_account" in st.secrets:
            from google.oauth2.service_account import Credentials
            scope = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            creds_dict = dict(st.secrets["gcp_service_account"])
            return Credentials.from_service_account_info(creds_dict, scopes=scope)
    except Exception as e:
        st.error(f"Errore configurazione credenziali: {e}")
    return None

def scrivi_cella_per_gid(gid, cell_address, value, target_sheet_id=SHEET_ID):
    """Scrive un valore in una cella specifica cercando il foglio tramite GID e ID del documento"""
    try:
        creds = ottieni_credenziali()
        if creds:
            client = gspread.authorize(creds)
            sheet = client.open_by_key(target_sheet_id)
            ws = next((w for w in sheet.worksheets() if str(w.id).strip() == str(gid).strip()), None)
            if ws:
                ws.update_acell(cell_address, value)
    except Exception as e:
        st.error(f"Errore durante la scrittura su Google Sheets: {e}")

# 2. CSS Styling
st.markdown("""
    <style>
    .stApp { background-color: #000; }
    h1, h2, h3, p { color: #fff !important; text-align: center; }
    
    /* Hide sidebar */
    [data-testid="stSidebar"] { display: none; }
    
    /* Navigation buttons style */
    div.stButton > button {
        width: 100%;
        background-color: #111;
        color: white;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 8px;
        font-weight: bold;
        font-size: 13px;
        transition: 0.2s;
    }
    div.stButton > button:hover {
        background-color: #222;
        border-color: #2ecc71;
        color: #2ecc71;
    }

    /* Standard Table Style */
    .custom-table {
        width: 100%;
        max-width: 600px;
        margin: 0 auto 20px auto;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #333;
        font-family: sans-serif;
    }
    .custom-table th {
        background-color: #222;
        color: #fff;
        padding: 10px 14px;
        text-align: center;
        border-bottom: 1px solid #444;
        font-size: 16px;
    }
    .custom-table td {
        background-color: #111;
        color: #ddd;
        padding: 10px 14px;
        border-bottom: 1px solid #222;
        text-align: center;
    }
    .custom-table td:first-child {
        text-align: left; 
    }
    .custom-table tr:last-child td {
        border-bottom: none;
    }

    /* Leaderboard Table Style */
    .ranking-table {
        width: 100%;
        max-width: 450px;
        margin: 0 auto 20px auto;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #333;
        font-family: sans-serif;
    }
    .ranking-table th {
        background-color: #222;
        color: #fff;
        padding: 10px 14px;
        text-align: center;
        border-bottom: 1px solid #444;
        font-size: 16px;
    }
    .ranking-table td {
        background-color: #111;
        color: #ddd;
        padding: 10px 14px;
        border-bottom: 1px solid #222;
        text-align: center;
    }
    .ranking-table td:first-child {
        text-align: left; 
    }
    .ranking-table tr:last-child td {
        border-bottom: none;
    }
    .ranking-table tbody tr:first-child td {
        color: #2ecc71 !important;
        font-weight: bold !important;
    }

    /* Stat Cards */
    .stat-card {
        background-color: #111;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        margin-bottom: 10px;
    }
    .stat-label {
        color: #888;
        font-size: 0.75rem;
        font-weight: bold;
        margin-bottom: 4px;
    }
    .stat-value {
        color: #fff;
        font-size: 1.1rem;
        font-weight: bold;
    }

    /* Larger Logo Style */
    .logo-container img {
        max-width: 350px;
        width: 100%;
        display: block;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Logo
col_l1, col_l2, col_l3 = st.columns([1, 10, 1])
with col_l2:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.title("EURO CUP")
    st.markdown('</div>', unsafe_allow_html=True)

# 4. Initialize session state for pages
if "page" not in st.session_state:
    st.session_state.page = "Leaderboard"

# 5. Horizontal Navigation Menu (7 Pulsanti)
st.write("")
b1, b2, b3, b4, b5, b6, b7 = st.columns(7)

with b1:
    if st.button("🏆\nLeader", use_container_width=True):
        st.session_state.page = "Leaderboard"
with b2:
    if st.button("📜\nRules", use_container_width=True):
        st.session_state.page = "Regole"
with b3:
    if st.button("⚔️\nScrims 1", use_container_width=True):
        st.session_state.page = "Scrims 1"
with b4:
    if st.button("⚔️\nScrims 2", use_container_width=True):
        st.session_state.page = "Scrims 2"
with b5:
    if st.button("👤\nPlayer", use_container_width=True):
        st.session_state.page = "Risultati Giocatore"
with b6:
    if st.button("🎯\nPersonal", use_container_width=True):
        st.session_state.page = "PERSONAL STATS"
with b7:
    if st.button("📊\nStat Comp", use_container_width=True):
        st.session_state.page = "STAT COMP"

st.write("---")

# 6. Data loading function
@st.cache_data(ttl=600)
def load_data(gid):
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}'
    return pd.read_csv(url)

# Standard table renderer
def render_custom_table(df_sub, headers):
    html = f'<table class="custom-table"><thead><tr>'
    for h in headers:
        html += f'<th>{h}</th>'
    html += '</tr></thead><tbody>'
    for _, row in df_sub.iterrows():
        html += '<tr>'
        for val in row:
            v_str = "" if pd.isna(val) or str(val).lower() == "nan" else str(val)
            html += f'<td>{v_str}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

# Leaderboard table renderer
def render_ranking_table(df_sub, headers):
    html = f'<table class="ranking-table"><thead><tr>'
    for h in headers:
        html += f'<th>{h}</th>'
    html += '</tr></thead><tbody>'
    for _, row in df_sub.iterrows():
        html += '<tr>'
        for val in row:
            v_str = "" if pd.isna(val) or str(val).lower() == "nan" else str(val)
            html += f'<td>{v_str}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

# General function to render Scrims tables
def render_scrims_tables(gid, scrim_title, team_coords, game_coords_list, summary_coords, overall_coords):
    st.markdown(f"<h1 style='text-align: center;'>⚔️ {scrim_title} Results</h1>", unsafe_allow_html=True)
    st.write("---")
    
    df = load_data(gid)
    
    try:
        t_start, t_end, t_col = team_coords
        teams = df.iloc[t_start:t_end, t_col].dropna().astype(str).reset_index(drop=True)
        teams = teams[teams.str.strip() != ""]
    except Exception:
        teams = pd.Series(["Team"] * 8)

    num_rows = len(teams)

    for idx, (r_start, r_end, c_start, c_end) in enumerate(game_coords_list, start=1):
        st.markdown(f"<h3 style='text-align: center;'>Game {idx}</h3>", unsafe_allow_html=True)
        try:
            val_df = df.iloc[r_start:r_start+num_rows, c_start:c_end].copy().fillna("")
            val_df.columns = ["Position", "Kills", "DMG", "Revive"]
            
            combined_df = pd.DataFrame({"Team": teams})
            for i, col in enumerate(val_df.columns):
                combined_df[col] = val_df.iloc[:, i].values

            st.markdown(render_custom_table(combined_df, ["Team", "Position", "Kills", "DMG", "Revive"]), unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading Game {idx} data: {e}")

    st.markdown("<h3 style='text-align: center;'>Summary & Adjustments</h3>", unsafe_allow_html=True)
    try:
        t7_r_start, _, t7_c_start, t7_c_end = summary_coords
        val_df = df.iloc[t7_r_start:t7_r_start+num_rows, t7_c_start:t7_c_end].copy().fillna("")
        
        combined_df = pd.DataFrame({"Team": teams})
        cols_t7 = ["Total Points", "Worst match dropped", "Remove Revive Penalty", "Adjusted Score"]
        for i, col in enumerate(cols_t7):
            if i < val_df.shape[1]:
                col_data = val_df.iloc[:, i].values
                if len(col_data) < num_rows:
                    col_data = list(col_data) + [""] * (num_rows - len(col_data))
                combined_df[col] = col_data[:num_rows]
            
        st.markdown(render_custom_table(combined_df, ["Team", "Total Points", "Worst Dropped", "No Revive Pen", "Adjusted"]), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading Table 7 data: {e}")

    st.markdown("<h3 style='text-align: center;'>Overall Stats</h3>", unsafe_allow_html=True)
    try:
        t8_r_start, _, t8_c_start, t8_c_end = overall_coords
        val_df = df.iloc[t8_r_start:t8_r_start+num_rows, t8_c_start:t8_c_end].copy().fillna("")
        
        combined_df = pd.DataFrame({"Team": teams})
        cols_t8 = ["Revive", "Kills", "DMG"]
        for i, col in enumerate(cols_t8):
            if i < val_df.shape[1]:
                col_data = val_df.iloc[:, i].values
                if len(col_data) < num_rows:
                    col_data = list(col_data) + [""] * (num_rows - len(col_data))
                combined_df[col] = col_data[:num_rows]
            
        st.markdown(render_custom_table(combined_df, ["Team", "Revive", "Kills", "DMG"]), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading Table 8 data: {e}")

# 7. Page Logic
page = st.session_state.page

if page == "Leaderboard":
    st.markdown("<h1 style='text-align: center;'>🏆 Leaderboard</h1>", unsafe_allow_html=True)
    st.write("---")
    
    df = load_data('316677537')
    
    st.markdown("<h3 style='text-align: center;'>Lobby 1</h3>", unsafe_allow_html=True)
    try:
        lobby1 = df.iloc[12:21, [5, 6]].copy()
        lobby1.columns = ["Team", "Points"]
        lobby1["Points"] = pd.to_numeric(lobby1["Points"], errors='coerce').fillna(0).astype(int)
        st.markdown(render_ranking_table(lobby1, ["Team", "Points"]), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error Lobby 1 Data: {e}")
        
    st.markdown("<h3 style='text-align: center;'>Lobby 2</h3>", unsafe_allow_html=True)
    try:
        lobby2 = df.iloc[12:21, [9, 10]].copy()
        lobby2.columns = ["Team", "Points"]
        lobby2["Points"] = pd.to_numeric(lobby2["Points"], errors='coerce').fillna(0).astype(int)
        st.markdown(render_ranking_table(lobby2, ["Team", "Points"]), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error Lobby 2 Data: {e}")

elif page == "Regole":
    st.markdown("<h1 style='text-align: center;'>📜 Rules & Info</h1>", unsafe_allow_html=True)
    st.write("---")
    
    scoring_html = """
    <table class="custom-table">
        <thead><tr><th colspan="2">SCORING SYSTEM</th></tr></thead>
        <tbody>
            <tr><td><b>Placement</b></td><td><b>Points</b></td></tr>
            <tr><td>1st</td><td>7 points</td></tr>
            <tr><td>2nd</td><td>5 points</td></tr>
            <tr><td>3rd</td><td>3 points</td></tr>
            <tr><td>4th</td><td>1 points</td></tr>
            <tr><td>5th (& +)</td><td>0 point</td></tr>
            <tr><td>1 Kill</td><td>1 point</td></tr>
            <tr><td>200 damages</td><td>1 point</td></tr>
            <tr><td>penalit revive</td><td>-0,3 points</td></tr>
        </tbody>
    </table>
    """
    st.markdown(scoring_html, unsafe_allow_html=True)

    info_html = """
    <table class="custom-table">
        <thead><tr><th colspan="2">INFO</th></tr></thead>
        <tbody>
            <tr><td>Map</td><td>EURO CUP MAPS</td></tr>
            <tr><td>Ping</td><td>EU</td></tr>
            <tr><td>Pod Pul</td><td>Allowed</td></tr>
            <tr><td>Items +/</td><td>Harmonica + /SPR -</td></tr>
            <tr><td>Games</td><td>6</td></tr>
            <tr><td colspan="2" style="font-weight: bold; color: #2ecc71;">“The worst game will NOT be counted” ✅</td></tr>
        </tbody>
    </table>
    """
    st.markdown(info_html, unsafe_allow_html=True)

    zone_html = """
    <table class="custom-table">
        <thead><tr><th colspan="2">ZONE SETTINGS</th></tr></thead>
        <tbody>
            <tr><td>Speed</td><td>130%</td></tr>
            <tr><td>Hold Time</td><td>60%</td></tr>
            <tr><td>Zone Damag</td><td>130%</td></tr>
        </tbody>
    </table>
    """
    st.markdown(zone_html, unsafe_allow_html=True)

elif page == "Scrims 1":
    s1_teams = (8, 16, 4) 
    s1_games = [
        (8, 16, 5, 9),    
        (8, 16, 10, 14),    
        (8, 16, 15, 19),    
        (8, 16, 20, 24),    
        (8, 16, 25, 29),    
        (8, 16, 30, 34)     
    ]
    s1_summary = (8, 16, 35, 40)  
    s1_overall = (8, 16, 39, 42)  
    
    render_scrims_tables('547827980', "Scrims 1", s1_teams, s1_games, s1_summary, s1_overall)

elif page == "Scrims 2":
    s2_teams = (20, 28, 4) 
    s2_games = [
        (20, 28, 5, 9),    
        (20, 28, 10, 14),    
        (20, 28, 15, 19),    
        (20, 28, 20, 24),    
        (20, 28, 25, 29),    
        (20, 28, 30, 34)     
    ]
    s2_summary = (20, 28, 35, 40)  
    s2_overall = (20, 28, 39, 42)  
    
    render_scrims_tables('547827980', "Scrims 2", s2_teams, s2_games, s2_summary, s2_overall)

elif page == "Risultati Giocatore":
    st.markdown("<h1 style='text-align: center;'>👤 Player Results</h1>", unsafe_allow_html=True)
    st.write("---")
    
    df_player = load_data('717130980')
    headers_player = ["Player", "Kill", "DMG", "MVP", "DHAT", "ACC%"]
    cols = [2, 3, 6, 9, 12, 15]
    
    st.markdown("<h3 style='text-align: center;'>Lobby 1</h3>", unsafe_allow_html=True)
    try:
        lobby1_df = df_player.iloc[11:35, cols].copy()
        lobby1_df.columns = headers_player
        st.markdown(render_custom_table(lobby1_df, headers_player), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading Lobby 1 Player Data: {e}")
        
    st.markdown("<h3 style='text-align: center;'>Lobby 2</h3>", unsafe_allow_html=True)
    try:
        lobby2_df = df_player.iloc[41:65, cols].copy()
        lobby2_df.columns = headers_player
        st.markdown(render_custom_table(lobby2_df, headers_player), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading Lobby 2 Player Data: {e}")
    
# ==========================================
# --- SEZIONE: PERSONAL STATS ---
# ==========================================
elif page == "PERSONAL STATS":
    st.markdown("<div style='background-color: #0e1117; border: 2px solid #262730; border-radius: 12px; padding: 20px;'>", unsafe_allow_html=True)
    st.markdown("### 👤 Personal Stats Dashboard")

    target_ws = None
    current_d13_val = ""
    extracted_players = []

    try:
        creds = ottieni_credenziali()
        if creds:
            client = gspread.authorize(creds)
            sheet = client.open_by_key(SHEET_ID)
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
        scrivi_cella_per_gid(GID_PERSONAL_STATS, "D13", selected_d13_val, target_sheet_id=SHEET_ID)
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

            weapons_raw = target_ws.get("F27:L67")
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

    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# --- SEZIONE: STAT COMP ---
# ==========================================
elif page == "STAT COMP":
    st.markdown("<div style='background-color: #0e1117; border: 2px solid #262730; border-radius: 12px; padding: 20px;'>", unsafe_allow_html=True)
    st.markdown("### 📊 Stat Comp Dashboard")

    target_ws_comp = None
    current_d13_comp = ""
    extracted_players_comp = []

    try:
        creds = ottieni_credenziali()
        if creds:
            client = gspread.authorize(creds)
            sheet = client.open_by_key(SHEET_ID_COMP)
            target_ws_comp = next((ws for ws in sheet.worksheets() if str(ws.id).strip() == str(GID_STAT_COMP).strip()), None)
            
            if target_ws_comp:
                d13_raw = target_ws_comp.acell("D13").value
                if d13_raw is not None and str(d13_raw).strip() != "":
                    current_d13_comp = str(d13_raw).strip()
                
                col_c_values = target_ws_comp.get("C12:C60")
                for row in col_c_values:
                    if row and len(row) > 0:
                        p = str(row[0]).strip()
                        if p and p.lower() not in ["nan", "none", ""]:
                            extracted_players_comp.append(p)
                extracted_players_comp = list(dict.fromkeys(extracted_players_comp))
    except Exception as e:
        st.warning(f"Error reading initial Stat Comp sheet: {e}")

    if not extracted_players_comp:
        extracted_players_comp = ["No players available"]

    player_index_comp = 0
    if current_d13_comp in extracted_players_comp:
        player_index_comp = extracted_players_comp.index(current_d13_comp)

    selected_d13_comp = st.selectbox("Select Player", extracted_players_comp, index=player_index_comp, key="sb_player_d13_comp")
    
    if str(selected_d13_comp).strip().lower() != str(current_d13_comp).strip().lower():
        scrivi_cella_per_gid(GID_STAT_COMP, "D13", selected_d13_comp, target_sheet_id=SHEET_ID_COMP)
        st.rerun()

    with st.spinner("Updating data..."):
        time.sleep(0.2)

    st.markdown("---")

    def format_val_comp(val, is_percentage=False, decimals=2):
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

    comp_fired, comp_hit, comp_acc, comp_kill, comp_dmg, comp_mvp, comp_death = "0", "0", "0.00%", "0", "0", "0", "0"
    comp_faster_banana = "-"
    comp_deadliest_w, comp_deadliest_d, comp_deadliest_a = "-", "0", "0.00%"
    comp_weapon_rows = []

    try:
        if target_ws_comp:
            f16_l16 = target_ws_comp.get("F16:L16")
            if f16_l16 and len(f16_l16) > 0:
                row_vals = f16_l16[0]
                comp_fired = format_val_comp(row_vals[0] if len(row_vals) > 0 else 0)
                comp_hit = format_val_comp(row_vals[1] if len(row_vals) > 1 else 0)
                comp_acc = format_val_comp(row_vals[2] if len(row_vals) > 2 else 0, is_percentage=True)
                comp_kill = format_val_comp(row_vals[3] if len(row_vals) > 3 else 0)
                comp_dmg = format_val_comp(row_vals[4] if len(row_vals) > 4 else 0)
                comp_mvp = format_val_comp(row_vals[5] if len(row_vals) > 5 else 0)
                comp_death = format_val_comp(row_vals[6] if len(row_vals) > 6 else 0)

            j18_l18 = target_ws_comp.get("J18:L18")
            if j18_l18 and len(j18_l18) > 0 and len(j18_l18[0]) > 0:
                comp_faster_banana = format_val_comp(j18_l18[0][0])

            h20_l21 = target_ws_comp.get("H20:L21")
            if h20_l21 and len(h20_l21) > 0:
                raw_w = h20_l21[0][0] if len(h20_l21[0]) > 0 else "-"
                comp_deadliest_w = str(raw_w).strip() if raw_w and str(raw_w).strip().lower() not in ["nan", "none", ""] else "-"
                
                if len(h20_l21) > 1:
                    comp_deadliest_d = format_val_comp(h20_l21[1][3] if len(h20_l21[1]) > 3 else 0)
                    comp_deadliest_a = format_val_comp(h20_l21[1][4] if len(h20_l21[1]) > 4 else 0, is_percentage=True)

            weapons_raw = target_ws_comp.get("F27:L67")
            if weapons_raw:
                for r_data in weapons_raw:
                    if r_data and len(r_data) > 0:
                        w_name = str(r_data[0]).strip()
                        if w_name and w_name.upper() not in ["NAN", "NONE", ""]:
                            comp_weapon_rows.append({
                                "WEAPON": w_name,
                                "TOT SHOTS": format_val_comp(r_data[1] if len(r_data) > 1 else 0, is_percentage=False),
                                "SHOT HIT": format_val_comp(r_data[2] if len(r_data) > 2 else 0, is_percentage=False),
                                "ACC%": format_val_comp(r_data[3] if len(r_data) > 3 else 0, is_percentage=True),
                                "DMG": format_val_comp(r_data[4] if len(r_data) > 4 else 0, is_percentage=False),
                                "HEADSHOT": format_val_comp(r_data[5] if len(r_data) > 5 else 0, is_percentage=False),
                                "MAX DISTANCE": format_val_comp(r_data[6] if len(r_data) > 6 else 0, is_percentage=False)
                            })
    except Exception as e:
        st.warning(f"Error reading Stat Comp dashboard data: {e}")

    st.markdown("<h4 style='color: #93c5fd; font-size: 1rem;'>MATCH SUMMARY</h4>", unsafe_allow_html=True)
    c_grid1, c_grid2, c_grid3 = st.columns(3)
    
    with c_grid1:
        st.markdown(f"<div class='stat-card'><div class='stat-label'>FIRED</div><div class='stat-value'>{comp_fired}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card'><div class='stat-label'>ACCURACY</div><div class='stat-value'>{comp_acc}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card'><div class='stat-label'>DMG</div><div class='stat-value'>{comp_dmg}</div></div>", unsafe_allow_html=True)
    with c_grid2:
        st.markdown(f"<div class='stat-card'><div class='stat-label'>SHOT HIT</div><div class='stat-value'>{comp_hit}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card'><div class='stat-label'>KILL</div><div class='stat-value'>{comp_kill}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card'><div class='stat-label'>MVP</div><div class='stat-value'>{comp_mvp}</div></div>", unsafe_allow_html=True)
    with c_grid3:
        st.markdown(f"<div class='stat-card'><div class='stat-label'>DEATH</div><div class='stat-value'>{comp_death}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card'><div class='stat-label'>FASTER BANANA</div><div class='stat-value'>{comp_faster_banana}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<h4 style='color: #93c5fd; font-size: 1rem;'>DEADLIEST WEAPON</h4>", unsafe_allow_html=True)
    dw_col1, dw_col2, dw_col3 = st.columns(3)
    with dw_col1:
        st.markdown(f"<div class='stat-card'><div class='stat-label'>WEAPON</div><div class='stat-value' style='font-size: 0.85rem;'>{comp_deadliest_w}</div></div>", unsafe_allow_html=True)
    with dw_col2:
        st.markdown(f"<div class='stat-card'><div class='stat-label'>DMG</div><div class='stat-value'>{comp_deadliest_d}</div></div>", unsafe_allow_html=True)
    with dw_col3:
        st.markdown(f"<div class='stat-card'><div class='stat-label'>ACC%</div><div class='stat-value'>{comp_deadliest_a}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<h4 style='color: #93c5fd; text-align: center;'>WEAPON PERFORMANCE</h4>", unsafe_allow_html=True)
    
    if comp_weapon_rows:
        df_comp_weapons_final = pd.DataFrame(comp_weapon_rows)
    else:
        df_comp_weapons_final = pd.DataFrame(columns=["WEAPON", "TOT SHOTS", "SHOT HIT", "ACC%", "DMG", "HEADSHOT", "MAX DISTANCE"])

    st.dataframe(df_comp_weapons_final, use_container_width=True, hide_index=True)

    st.markdown("</div>", unsafe_allow_html=True)
