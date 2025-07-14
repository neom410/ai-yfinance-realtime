import openai
from typing import Dict, List, Optional, Union
import json
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import pandas as pd

load_dotenv()

class FinancialAIGenerator:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.logger = logging.getLogger(__name__)
        
    def generate_market_analysis(self, market_data: Dict, analysis_type: str = "comprehensive") -> str:
        """Genera analisi di mercato basata sui dati"""
        try:
            # Prepara i dati per l'analisi
            formatted_data = self._format_data_for_analysis(market_data)
            
            prompt = self._create_analysis_prompt(formatted_data, analysis_type)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sei un analista finanziario esperto specializzato in analisi di mercato e trading. Fornisci analisi dettagliate, accurate e actionable basate sui dati forniti."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Errore nella generazione dell'analisi: {e}")
            return f"Errore nella generazione dell'analisi: {str(e)}"
    
    def generate_stock_prediction(self, symbol: str, historical_data: Dict, timeframe: str = "1-week") -> str:
        """Genera previsioni per un singolo titolo"""
        try:
            # Prepara i dati per la previsione
            formatted_data = self._format_stock_data_for_prediction(symbol, historical_data)
            
            prompt = f"""
            Analizza i seguenti dati storici per {symbol} e genera una previsione per {timeframe}:
            
            {formatted_data}
            
            Fornisci:
            1. **Previsione del prezzo** per {timeframe}
            2. **Livello di confidenza** (1-10)
            3. **Fattori chiave** che influenzano la previsione
            4. **Livelli di supporto e resistenza**
            5. **Strategia di trading consigliata**
            6. **Gestione del rischio**
            7. **Catalizzatori potenziali** da monitorare
            
            Formato della risposta: Strutturata con sezioni chiare e raccomandazioni specifiche.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sei un analista quantitativo esperto in previsioni di mercato. Usa analisi tecnica e fondamentale per fare previsioni accurate e conservative."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,
                temperature=0.6
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Errore nella generazione della previsione per {symbol}: {e}")
            return f"Errore nella generazione della previsione: {str(e)}"
    
    def generate_trading_signals(self, market_data: Dict) -> str:
        """Genera segnali di trading basati sui dati di mercato"""
        try:
            signals_data = self._analyze_trading_signals(market_data)
            
            prompt = f"""
            Basandoti sui seguenti segnali tecnici, genera raccomandazioni di trading:
            
            {json.dumps(signals_data, indent=2)}
            
            Per ogni titolo, fornisci:
            1. **Segnale**: BUY/SELL/HOLD
            2. **Forza del segnale**: 1-5 stelle
            3. **Entry point** suggerito
            4. **Stop loss** consigliato
            5. **Target price**
            6. **Timeframe** raccomandato
            7. **Rationale** del segnale
            
            Ordina per forza del segnale decrescente.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sei un trader esperto che genera segnali di trading precisi basati su analisi tecnica. Sii conservativo e preciso nelle raccomandazioni."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.5
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Errore nella generazione dei segnali: {e}")
            return f"Errore nella generazione dei segnali: {str(e)}"
    
    def generate_portfolio_analysis(self, portfolio_data: Dict) -> str:
        """Genera analisi del portafoglio"""
        try:
            prompt = f"""
            Analizza il seguente portafoglio e fornisci raccomandazioni:
            
            {json.dumps(portfolio_data, indent=2)}
            
            Fornisci:
            1. **Performance Overview** - Rendimenti e metriche chiave
            2. **Risk Analysis** - Volatilità, VaR, correlazioni
            3. **Diversification Analysis** - Distribuzione settoriale e geografica
            4. **Rebalancing Suggestions** - Aggiustamenti consigliati
            5. **Risk Management** - Strategie di hedging
            6. **Opportunities** - Nuove posizioni da considerare
            7. **Threat Assessment** - Rischi da monitorare
            
            Sii specifico nelle raccomandazioni con percentuali e target.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sei un portfolio manager esperto che fornisce analisi dettagliate e raccomandazioni per l'ottimizzazione del portafoglio."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1800,
                temperature=0.6
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Errore nell'analisi del portafoglio: {e}")
            return f"Errore nell'analisi del portafoglio: {str(e)}"
    
    def generate_risk_assessment(self, market_data: Dict) -> str:
        """Genera valutazione del rischio di mercato"""
        try:
            risk_metrics = self._calculate_risk_metrics(market_data)
            
            prompt = f"""
            Valuta il rischio di mercato basandoti sui seguenti dati:
            
            {json.dumps(risk_metrics, indent=2)}
            
            Fornisci:
            1. **Market Risk Level** (Low/Medium/High)
            2. **Key Risk Factors** - Principali fonti di rischio
            3. **Volatility Analysis** - Analisi della volatilità
            4. **Correlation Risks** - Rischi di correlazione
            5. **Liquidity Assessment** - Valutazione della liquidità
            6. **Stress Scenarios** - Scenari di stress
            7. **Risk Mitigation** - Strategie di mitigazione
            8. **Early Warning Indicators** - Indicatori da monitorare
            
            Usa un linguaggio chiaro e fornisci raccomandazioni actionable.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sei un risk manager esperto che valuta i rischi di mercato e fornisce strategie di mitigazione."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1400,
                temperature=0.5
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Errore nella valutazione del rischio: {e}")
            return f"Errore nella valutazione del rischio: {str(e)}"
    
    def generate_sector_analysis(self, sector_data: Dict) -> str:
        """Genera analisi settoriale"""
        try:
            prompt = f"""
            Analizza la performance settoriale basandoti sui seguenti dati:
            
            {json.dumps(sector_data, indent=2)}
            
            Fornisci:
            1. **Sector Rankings** - Classifica dei settori per performance
            2. **Outperforming Sectors** - Settori in sovraperformance
            3. **Underperforming Sectors** - Settori in sottoperformance
            4. **Rotation Signals** - Segnali di rotazione settoriale
            5. **Economic Drivers** - Driver economici per settore
            6. **Investment Themes** - Temi di investimento emergenti
            7. **Sector Allocation** - Raccomandazioni di allocazione
            
            Includi analisi relative e assolute.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sei un analista settoriale esperto che identifica opportunità e rischi nei diversi settori di mercato."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1300,
                temperature=0.6
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Errore nell'analisi settoriale: {e}")
            return f"Errore nell'analisi settoriale: {str(e)}"
    
    def generate_market_commentary(self, market_summary: Dict, news_data: List[Dict] = None) -> str:
        """Genera commento di mercato giornaliero"""
        try:
            prompt = f"""
            Crea un commento di mercato professionale basato sui seguenti dati:
            
            **Market Summary:**
            {json.dumps(market_summary, indent=2)}
            
            **News Context:**
            {json.dumps(news_data[:5] if news_data else [], indent=2)}
            
            Struttura il commento con:
            1. **Market Overview** - Panoramica generale
            2. **Key Movements** - Movimenti principali
            3. **Driving Forces** - Forze motrici
            4. **Technical Outlook** - Outlook tecnico
            5. **Tomorrow's Watch** - Cosa monitorare domani
            6. **Trading Considerations** - Considerazioni per il trading
            
            Mantieni un tono professionale ma accessibile.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sei un commentatore di mercato esperto che scrive analisi quotidiane per investitori professionali e retail."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Errore nel commento di mercato: {e}")
            return f"Errore nel commento di mercato: {str(e)}"
    
    def _format_data_for_analysis(self, market_data: Dict) -> str:
        """Formatta i dati per l'analisi AI"""
        formatted = []
        
        for symbol, data in market_data.items():
            if data:
                summary = {
                    'symbol': symbol,
                    'price': data.get('current_price', 0),
                    'change_pct': data.get('price_change_percent', 0),
                    'volume_ratio': data.get('volume_analysis', {}).get('volume_ratio', 0),
                    'rsi': data.get('technical_indicators', {}).get('rsi', 50),
                    'trend': data.get('trend_analysis', {}).get('short_term_trend', 'neutral'),
                    'volatility': data.get('volatility', {}).get('daily_volatility', 0)
                }
                formatted.append(summary)
        
        return json.dumps(formatted, indent=2)
    
    def _format_stock_data_for_prediction(self, symbol: str, data: Dict) -> str:
        """Formatta i dati di un singolo titolo per le previsioni"""
        if not data:
            return f"Nessun dato disponibile per {symbol}"
        
        formatted = {
            'symbol': symbol,
            'current_metrics': {
                'price': data.get('current_price', 0),
                'change_pct': data.get('price_change_percent', 0),
                'volume': data.get('volume', 0),
                'market_cap': data.get('market_cap', 0)
            },
            'technical_indicators': data.get('technical_indicators', {}),
            'price_levels': data.get('price_levels', {}),
            'trend_analysis': data.get('trend_analysis', {}),
            'volatility': data.get('volatility', {}),
            'momentum': data.get('momentum', {})
        }
        
        return json.dumps(formatted, indent=2)
    
    def _analyze_trading_signals(self, market_data: Dict) -> Dict:
        """Analizza i segnali di trading dai dati di mercato"""
        signals = {}
        
        for symbol, data in market_data.items():
            if not data:
                continue
                
            technical = data.get('technical_indicators', {})
            trend = data.get('trend_analysis', {})
            
            # Calcola forza del segnale basata su indicatori multipli
            signal_strength = 0
            signal_type = 'HOLD'
            
            # RSI analysis
            rsi = technical.get('rsi', 50)
            if rsi > 70:
                signal_strength -= 1  # Overbought
            elif rsi < 30:
                signal_strength += 1  # Oversold
                
            # Trend analysis
            short_trend = trend.get('short_term_trend', 'neutral')
            if short_trend == 'bullish':
                signal_strength += 1
            elif short_trend == 'bearish':
                signal_strength -= 1
                
            # MACD analysis
            macd = technical.get('macd', {})
            if macd.get('histogram', 0) > 0:
                signal_strength += 0.5
            else:
                signal_strength -= 0.5
                
            # Determina il tipo di segnale
            if signal_strength > 1:
                signal_type = 'BUY'
            elif signal_strength < -1:
                signal_type = 'SELL'
                
            signals[symbol] = {
                'signal': signal_type,
                'strength': abs(signal_strength),
                'rsi': rsi,
                'trend': short_trend,
                'macd': macd,
                'current_price': data.get('current_price', 0)
            }
        
        return signals
    
    def _calculate_risk_metrics(self, market_data: Dict) -> Dict:
        """Calcola metriche di rischio dal mercato"""
        volatilities = []
        correlations = []
        
        for symbol, data in market_data.items():
            if data and 'volatility' in data:
                vol = data['volatility'].get('daily_volatility', 0)
                if vol > 0:
                    volatilities.append(vol)
        
        if volatilities:
            avg_volatility = sum(volatilities) / len(volatilities)
            max_volatility = max(volatilities)
            
            risk_level = 'Low'
            if avg_volatility > 0.03:
                risk_level = 'High'
            elif avg_volatility > 0.02:
                risk_level = 'Medium'
        else:
            avg_volatility = 0
            max_volatility = 0
            risk_level = 'Unknown'
        
        return {
            'average_volatility': avg_volatility,
            'maximum_volatility': max_volatility,
            'risk_level': risk_level,
            'market_count': len([d for d in market_data.values() if d]),
            'high_vol_count': len([v for v in volatilities if v > 0.025])
        }
    
    def _create_analysis_prompt(self, formatted_data: str, analysis_type: str) -> str:
        """Crea il prompt per l'analisi basato sul tipo richiesto"""
        base_prompt = f"""
        Analizza i seguenti dati di mercato:
        
        {formatted_data}
        
        """
        
        if analysis_type == "comprehensive":
            return base_prompt + """
            Fornisci un'analisi completa che includa:
            1. **Panoramica generale del mercato**
            2. **Analisi dei trend principali**
            3. **Titoli in evidenza** (positivi e negativi)
            4. **Segnali tecnici importanti**
            5. **Livelli di supporto e resistenza chiave**
            6. **Analisi del volume e liquidità**
            7. **Outlook a breve termine**
            8. **Raccomandazioni operative**
            
            Usa un linguaggio professionale ma accessibile.
            """
        elif analysis_type == "technical":
            return base_prompt + """
            Concentrati sull'analisi tecnica:
            1. **Pattern tecnici identificati**
            2. **Indicatori momentum**
            3. **Livelli critici di prezzo**
            4. **Segnali di entry/exit**
            5. **Forza relativa dei titoli**
            """
        elif analysis_type == "quick":
            return base_prompt + """
            Fornisci un'analisi rapida e concisa:
            1. **Sentiment generale**
            2. **Top 3 opportunità**
            3. **Top 3 rischi**
            4. **Azione raccomandata**
            """
        else:
            return base_prompt + "Fornisci un'analisi bilanciata del mercato con focus su opportunità e rischi."
