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
        st.warning("Nessun dato disponibile per l'analisi AI")
        return
    
    # Controllo API key
    if not os.getenv('OPENAI_API_KEY'):
        st.warning("⚠️ API Key OpenAI non configurata. Configura la variabile OPENAI_API_KEY nel file .env")
        return
    
    ai_tabs = st.tabs(["📊 Market Analysis", "🎯 Trading Signals", "🔮 Predictions", "💭 Sentiment"])
    
    # Market Analysis
    with ai_tabs[0]:
        with st.spinner("🧠 Generando analisi di mercato..."):
            try:
                analysis = st.session_state.ai_generator.generate_market_analysis(
                    processed_data, 
                    config['analysis_type']
                )
                st.markdown(analysis)
            except Exception as e:
                st.error(f"Errore nell'analisi di mercato: {str(e)}")
    
    # Trading Signals
    with ai_tabs[1]:
        if config['enable_signals']:
            with st.spinner("📡 Generando segnali di trading..."):
                try:
                    signals = st.session_state.ai_generator.generate_trading_signals(processed_data)
                    st.markdown(signals)
                except Exception as e:
                    st.error(f"Errore nei segnali di trading: {str(e)}")
        else:
            st.info("Segnali di trading disabilitati. Abilitali nella sidebar.")
    
    # Predictions
    with ai_tabs[2]:
        if config['enable_predictions']:
            render_predictions(processed_data)
        else:
            st.info("Previsioni disabilitate. Abilitale nella sidebar.")
    
    # Sentiment Analysis
    with ai_tabs[3]:
        if config['enable_sentiment']:
            render_sentiment_analysis(processed_data)
        else:
            st.info("Analisi sentiment disabilitata. Abilitala nella sidebar.")

def render_predictions(processed_data):
    """Renderizza sezione previsioni"""
    st.subheader("🔮 AI Predictions")
    
    # Selezione simbolo per previsione dettagliata
    valid_symbols = [symbol for symbol, data in processed_data.items() if data]
    
    if valid_symbols:
        selected_symbol = st.selectbox("Seleziona simbolo per previsione dettagliata:", valid_symbols)
        
        if selected_symbol and processed_data[selected_symbol]:
            col1, col2 = st.columns(2)
            
            with col1:
                timeframe = st.selectbox("Timeframe previsione:", ["1-day", "1-week", "1-month"])
            
            with col2:
                if st.button("🔮 Genera Previsione"):
                    with st.spinner("Generando previsione..."):
                        try:
                            prediction = st.session_state.ai_generator.generate_stock_prediction(
                                selected_symbol, 
                                processed_data[selected_symbol], 
                                timeframe
                            )
                            st.markdown(prediction)
                        except Exception as e:
                            st.error(f"Errore nella previsione: {str(e)}")
            
            # Machine Learning Prediction
            if 'history' in processed_data[selected_symbol]:
                history = processed_data[selected_symbol]['history']
                if len(history) >= 100:
                    st.subheader("📈 ML Price Prediction")
                    
                    with st.spinner("Calcolando previsione ML..."):
                        try:
                            ml_prediction = st.session_state.ai_analyzer.predict_price_movement(
                                selected_symbol, 
                                history
                            )
                            
                            if 'error' not in ml_prediction:
                                render_ml_prediction_results(ml_prediction)
                            else:
                                st.error(ml_prediction['error'])
                        except Exception as e:
                            st.error(f"Errore nella previsione ML: {str(e)}")

def render_ml_prediction_results(prediction):
    """Renderizza risultati previsione ML"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Prezzo Previsto",
            f"${prediction['predicted_price']:.2f}",
            f"{prediction['predicted_change_percent']:+.2f}%"
        )
    
    with col2:
        st.metric(
            "Confidenza",
            f"{prediction['confidence_score']:.1f}%"
        )
    
    with col3:
        st.metric(
            "R² Score",
            f"{prediction['model_accuracy']['r2_score']:.3f}"
        )
    
    # Feature importance
    if 'feature_importance' in prediction:
        st.subheader("📊 Feature Importance")
        
        importance_df = pd.DataFrame(
            list(prediction['feature_importance'].items()),
            columns=['Feature', 'Importance']
        ).sort_values('Importance', ascending=False).head(10)
        
        fig = px.bar(
            importance_df, 
            x='Importance', 
            y='Feature',
            orientation='h',
            title="Top 10 Features più Importanti"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def render_sentiment_analysis(processed_data):
    """Renderizza analisi sentiment"""
    st.subheader("💭 Market Sentiment Analysis")
    
    with st.spinner("Analizzando sentiment del mercato..."):
        try:
            sentiment_data = st.session_state.ai_analyzer.analyze_sentiment_indicators(processed_data)
            
            if 'error' not in sentiment_data:
                render_sentiment_dashboard(sentiment_data)
            else:
                st.error(sentiment_data['error'])
        except Exception as e:
            st.error(f"Errore nell'analisi sentiment: {str(e)}")

def render_sentiment_dashboard(sentiment_data):
    """Renderizza dashboard del sentiment"""
    # Overall Sentiment
    overall = sentiment_data.get('overall_sentiment', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sentiment_color = get_sentiment_color(overall.get('sentiment', 'Neutral'))
        st.markdown(f"""
        <div class="metric-card">
            <h4>Overall Sentiment</h4>
            <h3 style="color: {sentiment_color}">{overall.get('sentiment', 'Neutral')}</h3>
            <p>Score: {overall.get('score', 0):.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        fg_index = sentiment_data.get('fear_greed_index', {})
        fg_color = get_fear_greed_color(fg_index.get('sentiment', 'Neutral'))
        st.markdown(f"""
        <div class="metric-card">
            <h4>Fear & Greed Index</h4>
            <h3 style="color: {fg_color}">{fg_index.get('sentiment', 'Neutral')}</h3>
            <p>Score: {fg_index.get('score', 50):.1f}/100</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        breadth = sentiment_data.get('advance_decline_ratio', {})
        st.markdown(f"""
        <div class="metric-card">
            <h4>Market Breadth</h4>
            <h3>{breadth.get('market_breadth', 'neutral').title()}</h3>
            <p>A/D Ratio: {breadth.get('ad_line', 0):.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Dettagli sentiment
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Advance/Decline")
        ad_data = sentiment_data.get('advance_decline_ratio', {})
        
        fig = go.Figure(data=[
            go.Bar(
                x=['Advancing', 'Declining', 'Unchanged'],
                y=[ad_data.get('advancing', 0), ad_data.get('declining', 0), ad_data.get('unchanged', 0)],
                marker_color=['green', 'red', 'gray']
            )
        ])
        fig.update_layout(title="Market Breadth", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Volume Analysis")
        vol_data = sentiment_data.get('volume_sentiment', {})
        
        vol_sentiment = vol_data.get('volume_sentiment', 'neutral')
        vol_color = 'green' if vol_sentiment == 'bullish' else 'red' if vol_sentiment == 'bearish' else 'gray'
        
        fig = go.Figure(data=[
            go.Bar(
                x=['High Vol Up', 'High Vol Down'],
                y=[vol_data.get('high_volume_up', 0), vol_data.get('high_volume_down', 0)],
                marker_color=['green', 'red']
            )
        ])
        fig.update_layout(title="Volume Sentiment", height=300)
        st.plotly_chart(fig, use_container_width=True)

def render_pattern_analysis(processed_data):
    """Renderizza analisi pattern"""
    st.header("🎯 Pattern Recognition")
    
    # Selezione simbolo
    valid_symbols = [symbol for symbol, data in processed_data.items() if data and 'history' in data]
    
    if valid_symbols:
        selected_symbol = st.selectbox("Seleziona simbolo per pattern analysis:", valid_symbols)
        
        if selected_symbol:
            history = processed_data[selected_symbol]['history']
            
            with st.spinner("Analizzando pattern..."):
                try:
                    patterns = st.session_state.ai_analyzer.analyze_price_patterns(history)
                    
                    if 'error' not in patterns:
                        render_pattern_results(patterns)
                    else:
                        st.error(patterns['error'])
                except Exception as e:
                    st.error(f"Errore nell'analisi pattern: {str(e)}")

def render_pattern_results(patterns):
    """Renderizza risultati pattern analysis"""
    # Support & Resistance
    if 'support_resistance' in patterns:
        sr_data = patterns['support_resistance']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔴 Resistance Levels")
            for level in sr_data.get('resistance_levels', []):
                st.write(f"${level:.2f}")
        
        with col2:
            st.subheader("🟢 Support Levels")
            for level in sr_data.get('support_levels', []):
                st.write(f"${level:.2f}")
    
    # Breakouts
    if 'breakout_signals' in patterns:
        breakout = patterns['breakout_signals']
        
        st.subheader("📈 Breakout Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Upward Breakout", "Yes" if breakout.get('upward_breakout') else "No")
        
        with col2:
            st.metric("Downward Breakout", "Yes" if breakout.get('downward_breakout') else "No")
        
        with col3:
            st.metric("Volume Confirmation", "Yes" if breakout.get('volume_confirmation') else "No")

def get_sentiment_color(sentiment):
    """Ottiene colore per sentiment"""
    sentiment_colors = {
        'Strong Bullish': '#00C851',
        'Bullish': '#4CAF50',
        'Neutral': '#ffbb33',
        'Bearish': '#ff4444',
        'Strong Bearish': '#CC0000'
    }
    return sentiment_colors.get(sentiment, '#666666')

def get_fear_greed_color(sentiment):
    """Ottiene colore per Fear & Greed Index"""
    fg_colors = {
        'Extreme Fear': '#CC0000',
        'Fear': '#ff4444',
        'Neutral': '#ffbb33',
        'Greed': '#4CAF50',
        'Extreme Greed': '#00C851'
    }
    return fg_colors.get(sentiment, '#666666')

def render_news_section():
    """Renderizza sezione notizie (placeholder)"""
    st.header("📰 Market News")
    st.info("Sezione notizie in sviluppo. Verrà integrata con feed di notizie in tempo reale.")

def render_portfolio_section():
    """Renderizza sezione portfolio (placeholder)"""
    st.header("💼 Portfolio Analysis")
    st.info("Sezione portfolio in sviluppo. Permetterà di caricare e analizzare portafogli personali.")

def main():
    """Funzione principale dell'applicazione"""
    # Configura pagina
    configure_page()
    
    # Inizializza componenti
    initialize_components()
    
    # Render header
    render_header()
    
    # Render sidebar e ottieni configurazione
    config = render_sidebar()
    
    # Verifica se ci sono simboli da analizzare
    if not config['symbols']:
        st.warning("⚠️ Inserisci almeno un simbolo nella sidebar per iniziare l'analisi.")
        return
    
    try:
        # Carica dati
        processed_data, market_summary = load_market_data(config)
        
        # Render componenti principali
        render_market_overview(market_summary)
        
        if processed_data:
            render_stock_metrics(processed_data)
            render_ai_analysis(processed_data, config)
            
            # Pattern analysis (se abilitato)
            if config['enable_patterns']:
                render_pattern_analysis(processed_data)
        
        # Sezioni aggiuntive
        st.markdown("---")
        extra_tabs = st.tabs(["📰 News", "💼 Portfolio"])
        
        with extra_tabs[0]:
            render_news_section()
        
        with extra_tabs[1]:
            render_portfolio_section()
            
    except Exception as e:
        st.error(f"Errore nell'applicazione: {str(e)}")
        st.error("Verifica la configurazione e riprova.")

if __name__ == "__main__":
    main()
