import os
import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime, timedelta

# ==========================================
# 🎨 CONFIGURAZIONE PAGINA E STILE
# ==========================================
st.set_page_config(page_title="Scudo WAF - Area Clienti", page_icon="🛡️", layout="wide")

# CSS Personalizzato - Sincronizzato con il design "Trust & Security" della Landing
st.markdown("""
<style>
    /* Rimuove elementi di disturbo Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sfondo generale e tipografia */
    [data-testid="stAppViewContainer"] {
        background-color: #ffffff;
    }
    h1, h2, h3, h4 {
        color: #0f172a !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    
    /* Stile per i riquadri delle metriche (KPI) */
    [data-testid="stMetric"] {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricLabel"] > div {
        color: #64748b !important;
        font-weight: 600;
        font-size: 1rem;
    }
    [data-testid="stMetricValue"] > div {
        color: #0f172a !important;
        font-weight: 800;
    }

    /* Stile Bottoni Primari (Rosso Scudo) */
    .stButton > button {
        background-color: #e11d48 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #be123c !important;
        box-shadow: 0 4px 6px -1px rgba(225, 29, 72, 0.2) !important;
    }

    /* Stile Bottone Download (Blu Trust) */
    .stDownloadButton > button {
        background-color: #0f172a !important;
        color: white !important;
        border-radius: 8px !important;
    }
    .stDownloadButton > button:hover {
        background-color: #1e293b !important;
    }
    
    /* Stile campi di input */
    .stTextInput input {
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🗄️ COLLEGAMENTO DATABASE (Supabase)
# ==========================================
#SUPABASE_URL = "https://izghfwxmmeotrxpjbeym.supabase.co"
#SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml6Z2hmd3htbWVvdHJ4cGpiZXltIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIxNTMzMzgsImV4cCI6MjA5NzcyOTMzOH0.LtxvympGKfgaJuEf0l6f9qMbLYyhMldM-2v6NDpxRYI"

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

# ==========================================
# 🔑 SISTEMA DI AUTENTICAZIONE (Login Clienti)
# ==========================================
def controlla_autenticazione():
    if st.session_state.get("autenticato", False):
        return True

    # Schermata di Login centrata
    st.write("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🛡️ Scudo WAF</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #64748b !important; font-weight: 500 !important;'>Area Clienti Sicura</h4>", unsafe_allow_html=True)
        st.write("")
        
        with st.form("login_form"):
            chiave_inserita = st.text_input("La tua API Key Segreta", type="password", placeholder="Es. sk_live_...")
            pulsante_login = st.form_submit_button("Accedi alla Dashboard", use_container_width=True)

            if pulsante_login:
                if chiave_inserita:
                    risposta_chiave = supabase.table("api_keys").select("*").eq("key_string", chiave_inserita).execute()
                    
                    if len(risposta_chiave.data) > 0:
                        st.session_state["autenticato"] = True
                        st.session_state["api_key_cliente"] = chiave_inserita
                        st.rerun()
                    else:
                        st.error("❌ API Key non trovata o disattivata.")
                else:
                    st.warning("⚠️ Inserisci la tua API Key per continuare.")
                    
    return False

if not controlla_autenticazione():
    st.stop()

# ==========================================
# 🎨 INTERFACCIA GRAFICA DASHBOARD CLIENTE
# ==========================================
chiave_cliente = st.session_state["api_key_cliente"]

# Layout della testata
col_titolo, col_vuota, col_azioni = st.columns([6, 1, 4])
with col_titolo:
    st.title("Il tuo Pannello di Controllo")
    st.markdown("<p style='color: #64748b; font-size: 1.1rem;'>Monitoraggio in tempo reale del traffico protetto dall'AI.</p>", unsafe_allow_html=True)

with col_azioni:
    st.write("") 
    btn1, btn2 = st.columns(2)
    with btn1:
        if st.button("🔄 Aggiorna Dati", use_container_width=True):
            st.rerun()
    with btn2:
        if st.button("🚪 Disconnetti", use_container_width=True):
            st.session_state["autenticato"] = False
            st.session_state["api_key_cliente"] = ""
            st.rerun()

st.divider()

# ==========================================
# 📊 RECUPERO DATI E FILTRI
# ==========================================
filtro_tempo = st.radio("Filtra per periodo:", ["Sempre", "Ultimi 30 giorni", "Ultimi 7 giorni"], horizontal=True)

risposta = supabase.table("log_attacchi").select("*").eq("api_key_usata", chiave_cliente).order("created_at", desc=True).execute()
df = pd.DataFrame(risposta.data)

if not df.empty:
    df['created_at'] = pd.to_datetime(df['created_at'])
    now = datetime.now(df['created_at'].dt.tz)
    
    if filtro_tempo == "Ultimi 7 giorni":
        df = df[df['created_at'] >= (now - timedelta(days=7))]
    elif filtro_tempo == "Ultimi 30 giorni":
        df = df[df['created_at'] >= (now - timedelta(days=30))]

totale_attacchi = len(df)

# --- METRICHE IN EVIDENZA (KPI) ---
st.subheader("Riepilogo Sicurezza")
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(label="🛡️ Minacce Totali Bloccate", value=totale_attacchi)
kpi2.metric(label="⚙️ Stato WAF AI", value="Online 🟢")
kpi3.metric(label="⚡ Latenza Media Rete", value="< 45 ms")

st.divider()

if totale_attacchi > 0:
    # --- GRAFICI ---
    col_grafico1, col_grafico2 = st.columns(2)
    
    # 1. GRAFICO TEMPORALE (Serie storica)
    with col_grafico1:
        st.markdown("<h4 style='font-size: 1.2rem; color: #0f172a;'>Andamento Attacchi</h4>", unsafe_allow_html=True)
        attacchi_per_giorno = df.groupby(df['created_at'].dt.date).size().reset_index(name='conteggio')
        fig_linea = px.line(attacchi_per_giorno, x='created_at', y='conteggio', markers=True)
        
        # Design Premium Plotly
        fig_linea.update_layout(
            xaxis_title="", 
            yaxis_title="", 
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)",
            hovermode="x unified"
        )
        # Linea Rossa Scudo
        fig_linea.update_traces(line_color='#e11d48', line_width=3, marker=dict(size=8, color='#0f172a'))
        fig_linea.update_xaxes(showgrid=False)
        fig_linea.update_yaxes(gridcolor='#e2e8f0')
        st.plotly_chart(fig_linea, use_container_width=True)

    # 2. GRAFICO A TORTA (Tipologie)
    with col_grafico2:
        st.markdown("<h4 style='font-size: 1.2rem; color: #0f172a;'>Distribuzione Minacce</h4>", unsafe_allow_html=True)
        attacchi_per_tipo = df['tipo_attacco'].value_counts().reset_index()
        attacchi_per_tipo.columns = ['tipo', 'conteggio']
        
        # Colori in tema: Blu Navy, Rosso Scudo, Azzurro, Grigio
        colori_torta = ['#0f172a', '#e11d48', '#3b82f6', '#94a3b8']
        fig_torta = px.pie(attacchi_per_tipo, values='conteggio', names='tipo', hole=0.5, color_discrete_sequence=colori_torta)
        
        fig_torta.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        fig_torta.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_torta, use_container_width=True)

    st.divider()
    
    # --- TABELLA E DOWNLOAD CSV ---
    col_tab_titolo, col_tab_btn = st.columns([8, 2])
    with col_tab_titolo:
        st.subheader("Registro Dettagliato Attacchi")
    with col_tab_btn:
        csv_data = df[['created_at', 'tipo_attacco', 'payload_malevolo']].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Esporta in CSV",
            data=csv_data,
            file_name=f"report_waf_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    tabella_vista = df.copy()
    tabella_vista['created_at'] = tabella_vista['created_at'].dt.strftime('%d/%m/%Y %H:%M:%S')
    tabella_vista = tabella_vista.rename(columns={
        "created_at": "Data e Ora",
        "tipo_attacco": "Minaccia Rilevata",
        "payload_malevolo": "Testo (Corpo del Reato)"
    })
    
    colonne_da_mostrare = ["Data e Ora", "Minaccia Rilevata", "Testo (Corpo del Reato)"]
    st.dataframe(tabella_vista[colonne_da_mostrare], use_container_width=True, hide_index=True)

else:
    st.info("Nessun attacco registrato nel periodo selezionato. Il tuo sistema è al sicuro! ✅")