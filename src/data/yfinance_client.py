import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

# Importa i nostri moduli
from src.data.yfinance_client import YFinanceClient
from src.data.data_processor import DataProcessor
from src.ai.generators import FinancialAIGenerator
from src.ai.analyzers import FinancialAnalyzer

# Carica variabili d'ambiente
load_dotenv()

def initialize_components():
    """Inizializza i componenti principali"""
    if 'yf_client' not in st.session_state:
        st.session_state.yf_client = YFinanceClient()
    if 'data_processor' not in st.session_state:
        st.session_state.data_processor = DataProcessor()
    if 'ai_generator' not in st.session_state:
        st.session_state.ai_generator = FinancialAIGenerator()
    if 'ai_analyzer' not in st.session_state:
        st.session_state.ai_analyzer = FinancialAnalyzer()

def configure_page():
    """Configura la pagina Streamlit"""
    st.set_page_config(
        page_title="AI Financial Analysis Platform",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS personalizzato
    st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .positive { color: #00C851; }
    .negative { color: #ff4444; }
    .neutral { color: #ffbb33; }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Renderizza l'header dell'applicazione"""
    st.title("🤖 AI Financial Analysis Platform")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🕐 Last Update", datetime.now().strftime("%H:%M:%S"))
    with col2:
        st.metric("📊 Market Status", "Open" if datetime.now().hour < 16 else "Closed")
    with col3:
        if st.button("🔄 Refresh Data"):
            st.experimental_rerun()

def render_sidebar():
    """Renderizza la sidebar con i controlli"""
    st.sidebar.header("🛠️ Configurazione")
    
    # Selezione simboli
    symbols_input = st.sidebar.text_input(
        "Simboli (separati da virgola)", 
        value="AAPL,GOOGL,MSFT,AMZN,TSLA",
        help="Inserisci i ticker separati da virgola"
    )
    
    symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]
    
    # Periodo di analisi
    period = st.sidebar.selectbox(
        "Periodo di Analisi",
        ["1d", "5d", "1mo", "3mo", "6mo", "1y"],
        index=2
    )
    
    # Intervallo
    interval = st.sidebar.selectbox(
        "Intervallo",
        ["1m", "5m", "15m", "30m", "1h", "1d"],
        index=5
    )
    
    # Tipo di analisi
    analysis_type = st.sidebar.selectbox(
        "Tipo di Analisi AI",
        ["comprehensive", "technical", "quick"],
        index=0
    )
    
    # Abilitazioni
    st.sidebar.header("🔧 Funzionalità")
    enable_predictions = st.sidebar.checkbox("Previsioni AI", value=True)
    enable_signals = st.sidebar.checkbox("Segnali Trading", value=True)
    enable_sentiment = st.sidebar.checkbox("Analisi Sentiment", value=True)
    enable_patterns = st.sidebar.checkbox("Pattern Recognition", value=False)
    
    return {
        'symbols': symbols,
        'period': period,
        'interval': interval,
        'analysis_type': analysis_type,
        'enable_predictions': enable_predictions,
        'enable_signals': enable_signals,
        'enable_sentiment': enable_sentiment,
        'enable_patterns': enable_patterns
    }

def load_market_data(config):
    """Carica i dati di mercato"""
    with st.spinner("📡 Caricamento dati di mercato..."):
        # Ottieni dati real-time
        raw_data = st.session_state.yf_client.get_realtime_data(
            config['symbols'], 
            config['period'], 
            config['interval']
        )
        
        # Elabora i dati
        processed_data = st.session_state.data_processor.process_realtime_data(raw_data)
        
        # Ottieni riassunto mercato
        market_summary = st.session_state.yf_client.get_market_summary()
        
        return processed_data, market_summary

def render_market_overview(market_summary):
    """Renderizza panoramica del mercato"""
    st.header("🌍 Market Overview")
    
    if market_summary:
        cols = st.columns(len(market_summary))
        
        for i, (symbol, data) in enumerate(market_summary.items()):
            if data:
                with cols[i]:
                    change_color = "positive" if data['change'] >= 0 else "negative"
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{data['name']}</h4>
                        <h3>${data['current']:.2f}</h3>
                        <p class="{change_color}">
                            {data['change']:+.2f} ({data['change_percent']:+.2f}%)
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

def render_stock_metrics(processed_data):
    """Renderizza metriche dei singoli titoli"""
    st.header("📈 Stock Analysis")
    
    # Crea tabs per ogni titolo
    if processed_data:
        valid_symbols = [symbol for symbol, data in processed_data.items() if data]
        
        if valid_symbols:
            tabs = st.tabs(valid_symbols)
            
            for i, symbol in enumerate(valid_symbols):
                with tabs[i]:
                    render_individual_stock(symbol, processed_data[symbol])

def render_individual_stock(symbol, data):
    """Renderizza analisi per un singolo titolo"""
    col1, col2, col3, col4 = st.columns(4)
    
    # Metriche base
    with col1:
        st.metric(
            "Prezzo Attuale",
            f"${data['current_price']:.2f}",
            f"{data['price_change']:+.2f}"
        )
    
    with col2:
        st.metric(
            "Variazione %",
            f"{data['price_change_percent']:+.2f}%",
            delta_color="normal"
        )
    
    with col3:
        volume_ratio = data.get('volume_analysis', {}).get('volume_ratio', 1)
        st.metric(
            "Volume Ratio",
            f"{volume_ratio:.2f}x",
            "Alto" if volume_ratio > 1.2 else "Normale"
        )
    
    with col4:
        rsi = data.get('technical_indicators', {}).get('rsi', 50)
        rsi_status = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
        st.metric(
            "RSI",
            f"{rsi:.1f}",
            rsi_status
        )
    
    # Grafico dei prezzi
    render_price_chart(symbol, data)
    
    # Indicatori tecnici
    render_technical_indicators(data)

def render_price_chart(symbol, data):
    """Renderizza grafico dei prezzi"""
    if 'history' in data and not data['history'].empty:
        history = data['history']
        
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f'{symbol} - Prezzo e Volume', 'Volume'),
            row_width=[0.7, 0.3]
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=history.index,
                open=history['Open'],
                high=history['High'],
                low=history['Low'],
                close=history['Close'],
                name='Prezzo'
            ),
            row=1, col=1
        )
        
        # Media mobile
        if len(history) >= 20:
            sma_20 = history['Close'].rolling(20).mean()
            fig.add_trace(
                go.Scatter(
                    x=history.index,
                    y=sma_20,
                    mode='lines',
                    name='SMA 20',
                    line=dict(color='orange', width=1)
                ),
                row=1, col=1
            )
        
        # Volume
        colors = ['green' if close >= open else 'red' 
                 for close, open in zip(history['Close'], history['Open'])]
        
        fig.add_trace(
            go.Bar(
                x=history.index,
                y=history['Volume'],
                name='Volume',
                marker_color=colors
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=600,
            showlegend=True,
            xaxis_rangeslider_visible=False
        )
        
        st.plotly_chart(fig, use_container_width=True)

def render_technical_indicators(data):
    """Renderizza indicatori tecnici"""
    st.subheader("🔧 Technical Indicators")
    
    technical = data.get('technical_indicators', {})
    if technical:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Moving Averages**")
            for key, value in technical.items():
                if 'sma' in key or 'ema' in key:
                    if value:
                        st.write(f"{key.upper()}: ${value:.2f}")
        
        with col2:
            st.write("**Oscillators**")
            if 'rsi' in technical and technical['rsi']:
                st.write(f"RSI: {technical['rsi']:.1f}")
            
            if 'macd' in technical:
                macd_data = technical['macd']
                if isinstance(macd_data, dict):
                    st.write(f"MACD: {macd_data.get('macd', 0):.3f}")
                    st.write(f"Signal: {macd_data.get('signal', 0):.3f}")

def render_ai_analysis(processed_data, config):
    """Renderizza analisi AI"""
    st.header("🤖 AI Analysis")
    
    if not processed_data:
