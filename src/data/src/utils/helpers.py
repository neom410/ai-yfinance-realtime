import logging
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import json

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Configura il sistema di logging"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configura il livello di log
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configura handlers
    handlers = [logging.StreamHandler()]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers
    )
    
    return logging.getLogger(__name__)

def validate_symbols(symbols: List[str]) -> List[str]:
    """Valida e pulisce lista di simboli"""
    valid_symbols = []
    
    for symbol in symbols:
        # Rimuovi spazi e converti in maiuscolo
        clean_symbol = symbol.strip().upper()
        
        # Controlli base di validità
        if len(clean_symbol) >= 1 and len(clean_symbol) <= 6:
            if clean_symbol.isalnum() or '.' in clean_symbol or '^' in clean_symbol:
                valid_symbols.append(clean_symbol)
    
    return valid_symbols

def format_currency(value: float, currency: str = "USD") -> str:
    """Formatta valori monetari"""
    if abs(value) >= 1e12:
        return f"${value/1e12:.2f}T"
    elif abs(value) >= 1e9:
        return f"${value/1e9:.2f}B"
    elif abs(value) >= 1e6:
        return f"${value/1e6:.2f}M"
    elif abs(value) >= 1e3:
        return f"${value/1e3:.2f}K"
    else:
        return f"${value:.2f}"

def format_percentage(value: float, decimals: int = 2) -> str:
    """Formatta valori percentuali"""
    return f"{value:.{decimals}f}%"

def format_volume(volume: int) -> str:
    """Formatta volumi di trading"""
    if volume >= 1e9:
        return f"{volume/1e9:.2f}B"
    elif volume >= 1e6:
        return f"{volume/1e6:.2f}M"
    elif volume >= 1e3:
        return f"{volume/1e3:.2f}K"
    else:
        return str(volume)

def calculate_market_cap_category(market_cap: float) -> str:
    """Categorizza la capitalizzazione di mercato"""
    if market_cap >= 200e9:
        return "Mega Cap"
    elif market_cap >= 10e9:
        return "Large Cap"
    elif market_cap >= 2e9:
        return "Mid Cap"
    elif market_cap >= 300e6:
        return "Small Cap"
    elif market_cap >= 50e6:
        return "Micro Cap"
    else:
        return "Nano Cap"

def is_market_open() -> bool:
    """Controlla se il mercato è aperto (USA)"""
    now = datetime.now()
    
    # Controlla se è weekend
    if now.weekday() >= 5:  # Sabato = 5, Domenica = 6
        return False
    
    # Controlla orari di mercato (9:30 - 16:00 EST, approssimativo)
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    return market_open <= now <= market_close

def get_trading_days(start_date: datetime, end_date: datetime) -> List[datetime]:
    """Ottiene lista di giorni di trading tra due date"""
    trading_days = []
    current_date = start_date
    
    while current_date <= end_date:
        # Escludi weekend
        if current_date.weekday() < 5:
            trading_days.append(current_date)
        current_date += timedelta(days=1)
    
    return trading_days

def calculate_returns(prices: pd.Series) -> pd.Series:
    """Calcola i rendimenti percentuali"""
    return prices.pct_change().fillna(0)

def calculate_volatility(returns: pd.Series, annualize: bool = True) -> float:
    """Calcola la volatilità"""
    vol = returns.std()
    if annualize:
        vol *= np.sqrt(252)  # 252 giorni di trading all'anno
    return vol

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """Calcola lo Sharpe ratio"""
    excess_returns = returns.mean() * 252 - risk_free_rate
    volatility = calculate_volatility(returns)
    
    if volatility == 0:
        return 0
    
    return excess_returns / volatility

def calculate_max_drawdown(prices: pd.Series) -> Dict[str, float]:
    """Calcola il maximum drawdown"""
    peak = prices.expanding().max()
    drawdown = (prices - peak) / peak
    max_drawdown = drawdown.min()
    
    # Trova le date del drawdown
    max_dd_date = drawdown.idxmin()
    peak_date = peak.loc[:max_dd_date].idxmax()
    
    return {
        'max_drawdown': max_drawdown,
        'max_drawdown_percent': max_drawdown * 100,
        'peak_date': peak_date,
        'trough_date': max_dd_date
    }

def normalize_data(data: pd.Series, method: str = 'minmax') -> pd.Series:
    """Normalizza i dati"""
    if method == 'minmax':
        return (data - data.min()) / (data.max() - data.min())
    elif method == 'zscore':
        return (data - data.mean()) / data.std()
    else:
        raise ValueError("Method must be 'minmax' or 'zscore'")

def detect_outliers(data: pd.Series, method: str = 'iqr') -> pd.Series:
    """Rileva outliers nei dati"""
    if method == 'iqr':
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return (data < lower_bound) | (data > upper_bound)
    
    elif method == 'zscore':
        z_scores = np.abs((data - data.mean()) / data.std())
        return z_scores > 3
    
    else:
        raise ValueError("Method must be 'iqr' or 'zscore'")

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Divisione sicura che evita divisione per zero"""
    if denominator == 0 or pd.isna(denominator):
        return default
    return numerator / denominator

def clean_financial_data(data: pd.DataFrame) -> pd.DataFrame:
    """Pulisce i dati finanziari da valori anomali"""
    cleaned_data = data.copy()
    
    # Rimuovi righe con tutti NaN
    cleaned_data = cleaned_data.dropna(how='all')
    
    # Per le colonne numeriche, riempi NaN con il valore precedente
    numeric_columns = cleaned_data.select_dtypes(include=[np.number]).columns
    cleaned_data[numeric_columns] = cleaned_data[numeric_columns].fillna(method='forward')
    
    # Rimuovi outliers estremi per Volume (oltre 10 deviazioni standard)
    if 'Volume' in cleaned_data.columns:
        volume_mean = cleaned_data['Volume'].mean()
        volume_std = cleaned_data['Volume'].std()
        volume_threshold = volume_mean + 10 * volume_std
        cleaned_data.loc[cleaned_data['Volume'] > volume_threshold, 'Volume'] = volume_mean
    
    return cleaned_data

def get_risk_level(volatility: float) -> str:
    """Determina il livello di rischio basato sulla volatilità"""
    if volatility < 0.15:
        return "Low"
    elif volatility < 0.25:
        return "Medium"
    elif volatility < 0.40:
        return "High"
    else:
        return "Very High"

def categorize_stock_by_price(price: float) -> str:
    """Categorizza azione per fascia di prezzo"""
    if price < 5:
        return "Penny Stock"
    elif price < 25:
        return "Low Price"
    elif price < 100:
        return "Medium Price"
    elif price < 500:
        return "High Price"
    else:
        return "Very High Price"

def calculate_correlation_matrix(data: Dict[str, pd.Series]) -> pd.DataFrame:
    """Calcola matrice di correlazione tra più serie"""
    df = pd.DataFrame(data)
    return df.corr()

def find_similar_patterns(target_series: pd.Series, comparison_series: pd.Series, window: int = 20) -> List[Dict]:
    """Trova pattern simili tra due serie temporali"""
    similarities = []
    
    if len(target_series) < window or len(comparison_series) < window:
        return similarities
    
    # Normalizza le serie
    target_norm = normalize_data(target_series.tail(window))
    
    for i in range(len(comparison_series) - window + 1):
        segment = comparison_series.iloc[i:i+window]
        segment_norm = normalize_data(segment)
        
        # Calcola similarità usando correlazione
        correlation = target_norm.corr(segment_norm)
        
        if not pd.isna(correlation) and correlation > 0.7:  # Soglia di similarità
            similarities.append({
                'start_index': i,
                'end_index': i + window,
                'correlation': correlation,
                'start_date': segment.index[0] if hasattr(segment.index[0], 'date') else None
            })
    
    return sorted(similarities, key=lambda x: x['correlation'], reverse=True)

def create_summary_stats(data: pd.Series) -> Dict[str, float]:
    """Crea statistiche riassuntive per una serie"""
    return {
        'count': len(data),
        'mean': data.mean(),
        'median': data.median(),
        'std': data.std(),
        'min': data.min(),
        'max': data.max(),
        'q25': data.quantile(0.25),
        'q75': data.quantile(0.75),
        'skewness': data.skew(),
        'kurtosis': data.kurtosis()
    }

def export_analysis_to_json(analysis_data: Dict, filename: str = None) -> str:
    """Esporta analisi in formato JSON"""
    if filename is None:
        filename = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Converti oggetti datetime e numpy in formati serializzabili
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32)):
            return float(obj)
        elif pd.isna(obj):
            return None
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    try:
        with open(filename, 'w') as f:
            json.dump(analysis_data, f, indent=2, default=json_serializer)
        return f"Analisi esportata in {filename}"
    except Exception as e:
        return f"Errore nell'esportazione: {str(e)}"

def load_analysis_from_json(filename: str) -> Dict:
    """Carica analisi da file JSON"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Errore nel caricamento: {str(e)}")

def validate_api_key(api_key: str, service: str = "openai") -> bool:
    """Valida formato API key"""
    if not api_key:
        return False
    
    if service == "openai":
        return api_key.startswith("sk-") and len(api_key) > 20
    elif service == "alpha_vantage":
        return len(api_key) >= 8 and api_key.isalnum()
    
    return False

def create_backup(data: Dict, backup_dir: str = "backups") -> str:
    """Crea backup dei dati"""
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = os.path.join(backup_dir, f"backup_{timestamp}.json")
    
    return export_analysis_to_json(data, backup_filename)

def get_memory_usage() -> Dict[str, str]:
    """Ottiene informazioni sull'uso della memoria"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        'rss': format_currency(memory_info.rss / 1024 / 1024, "MB"),
        'vms': format_currency(memory_info.vms / 1024 / 1024, "MB"),
        'percent': f"{process.memory_percent():.2f}%"
    }

def benchmark_function(func, *args, **kwargs) -> Dict[str, Any]:
    """Benchmarka l'esecuzione di una funzione"""
    import time
    
    start_time = time.time()
    start_memory = get_memory_usage()
    
    try:
        result = func(*args, **kwargs)
        success = True
        error = None
    except Exception as e:
        result = None
        success = False
        error = str(e)
    
    end_time = time.time()
    end_memory = get_memory_usage()
    
    return {
        'success': success,
        'result': result,
        'error': error,
        'execution_time': end_time - start_time,
        'start_memory': start_memory,
        'end_memory': end_memory
    }

def create_config_template(filename: str = "config_template.json") -> str:
    """Crea template di configurazione"""
    config_template = {
        "api_keys": {
            "openai": "sk-your_openai_key_here",
            "alpha_vantage": "your_alpha_vantage_key_here"
        },
        "default_symbols": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"],
        "analysis_settings": {
            "default_period": "3mo",
            "default_interval": "1d",
            "enable_predictions": True,
            "enable_signals": True,
            "enable_sentiment": True,
            "enable_patterns": False
        },
        "risk_settings": {
            "max_position_size": 0.1,
            "stop_loss_percentage": 0.05,
            "take_profit_percentage": 0.15
        },
        "performance_settings": {
            "cache_timeout": 300,
            "max_requests_per_minute": 60,
            "parallel_processing": True
        }
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(config_template, f, indent=2)
        return f"Template di configurazione creato: {filename}"
    except Exception as e:
        return f"Errore nella creazione del template: {str(e)}"
