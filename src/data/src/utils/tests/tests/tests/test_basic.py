import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Aggiungi src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data.yfinance_client import YFinanceClient
from data.data_processor import DataProcessor
from utils.helpers import validate_symbols, format_currency, is_market_open

class TestYFinanceClient(unittest.TestCase):
    def setUp(self):
        self.client = YFinanceClient()
    
    def test_client_initialization(self):
        """Test inizializzazione client"""
        self.assertIsInstance(self.client, YFinanceClient)
        self.assertIsNotNone(self.client.logger)
    
    def test_get_realtime_data_valid_symbol(self):
        """Test recupero dati per simbolo valido"""
        data = self.client.get_realtime_data(['AAPL'])
        
        self.assertIsInstance(data, dict)
        self.assertIn('AAPL', data)
        
        if data['AAPL'] is not None:
            self.assertIn('current_price', data['AAPL'])
            self.assertIn('price_change_percent', data['AAPL'])
    
    def test_get_realtime_data_invalid_symbol(self):
        """Test recupero dati per simbolo non valido"""
        data = self.client.get_realtime_data(['INVALID_SYMBOL_XYZ'])
        
        self.assertIsInstance(data, dict)
        # Il simbolo potrebbe restituire None se non valido
    
    def test_get_market_summary(self):
        """Test recupero riassunto mercato"""
        summary = self.client.get_market_summary()
        
        self.assertIsInstance(summary, dict)
        # Dovrebbe contenere almeno un indice
        expected_indices = ['^GSPC', '^DJI', '^IXIC', '^VIX']
        has_valid_data = any(index in summary for index in expected_indices)
        self.assertTrue(has_valid_data)

class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = DataProcessor()
        
        # Crea dati di test
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        self.test_history = pd.DataFrame({
            'Open': 100 + np.cumsum(np.random.randn(len(dates)) * 0.5),
            'High': 105 + np.cumsum(np.random.randn(len(dates)) * 0.5),
            'Low': 95 + np.cumsum(np.random.randn(len(dates)) * 0.5),
            'Close': 100 + np.cumsum(np.random.randn(len(dates)) * 0.5),
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)
        
        # Assicurati che High >= Low e che i prezzi siano logici
        self.test_history['High'] = self.test_history[['Open', 'Close', 'High']].max(axis=1)
        self.test_history['Low'] = self.test_history[['Open', 'Close', 'Low']].min(axis=1)
    
    def test_calculate_technical_indicators(self):
        """Test calcolo indicatori tecnici"""
        indicators = self.processor._calculate_technical_indicators(self.test_history)
        
        self.assertIsInstance(indicators, dict)
        
        # Verifica presenza indicatori chiave
        expected_indicators = ['sma_20', 'rsi', 'macd']
        for indicator in expected_indicators:
            self.assertIn(indicator, indicators)
    
    def test_calculate_price_levels(self):
        """Test calcolo livelli di prezzo"""
        levels = self.processor._calculate_price_levels(self.test_history)
        
        self.assertIsInstance(levels, dict)
        self.assertIn('pivot_point', levels)
        self.assertIn('resistance_1', levels)
        self.assertIn('support_1', levels)
    
    def test_analyze_volume(self):
        """Test analisi volume"""
        volume_analysis = self.processor._analyze_volume(self.test_history)
        
        self.assertIsInstance(volume_analysis, dict)
        self.assertIn('current_volume', volume_analysis)
        self.assertIn('avg_volume_10', volume_analysis)
        self.assertIn('volume_trend', volume_analysis)
    
    def test_calculate_volatility(self):
        """Test calcolo volatilità"""
        volatility = self.processor._calculate_volatility(self.test_history)
        
        self.assertIsInstance(volatility, dict)
        self.assertIn('daily_volatility', volatility)
        self.assertIn('annualized_volatility', volatility)
        
        # La volatilità dovrebbe essere positiva
        self.assertGreater(volatility['daily_volatility'], 0)

class TestHelpers(unittest.TestCase):
    def test_validate_symbols(self):
        """Test validazione simboli"""
        # Test simboli validi
        valid_symbols = validate_symbols(['AAPL', 'googl', ' MSFT ', 'AMZN'])
        expected = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']
        self.assertEqual(valid_symbols, expected)
        
        # Test simboli non validi
        invalid_symbols = validate_symbols(['', '   ', 'TOOLONG', '123'])
        self.assertEqual(len(invalid_symbols), 1)  # Solo '123' potrebbe essere valido
    
    def test_format_currency(self):
        """Test formattazione valuta"""
        self.assertEqual(format_currency(1000), "$1.00K")
        self.assertEqual(format_currency(1000000), "$1.00M")
        self.assertEqual(format_currency(1000000000), "$1.00B")
        self.assertEqual(format_currency(1000000000000), "$1.00T")
        self.assertEqual(format_currency(123.45), "$123.45")
    
    def test_is_market_open(self):
        """Test controllo apertura mercato"""
        # Non possiamo testare completamente senza mockare datetime
        # ma possiamo verificare che restituisca un booleano
        result = is_market_open()
        self.assertIsInstance(result, bool)

class TestIntegration(unittest.TestCase):
    """Test di integrazione tra componenti"""
    
    def setUp(self):
        self.client = YFinanceClient()
        self.processor = DataProcessor()
    
    def test_full_pipeline(self):
        """Test pipeline completa: dati -> elaborazione"""
        # Ottieni dati
        symbols = ['AAPL']
        raw_data = self.client.get_realtime_data(symbols)
        
        # Elabora dati
        if raw_data['AAPL'] is not None:
            processed_data = self.processor.process_realtime_data(raw_data)
            
            self.assertIsInstance(processed_data, dict)
            self.assertIn('AAPL', processed_data)
            
            if processed_data['AAPL'] is not None:
                # Verifica che i dati elaborati contengano le sezioni attese
                expected_sections = ['technical_indicators', 'price_levels', 'volume_analysis']
                for section in expected_sections:
                    self.assertIn(section, processed_data['AAPL'])

class TestErrorHandling(unittest.TestCase):
    """Test gestione errori"""
    
    def setUp(self):
        self.client = YFinanceClient()
        self.processor = DataProcessor()
    
    def test_empty_data_handling(self):
        """Test gestione dati vuoti"""
        empty_data = {}
        result = self.processor.process_realtime_data(empty_data)
        self.assertEqual(result, {})
    
    def test_invalid_history_data(self):
        """Test gestione dati storici non validi"""
        empty_history = pd.DataFrame()
        
        # Dovrebbe gestire gracefully DataFrame vuoti
        indicators = self.processor._calculate_technical_indicators(empty_history)
        self.assertEqual(indicators, {})

class TestPerformance(unittest.TestCase):
    """Test di performance"""
    
    def test_large_dataset_processing(self):
        """Test elaborazione dataset grande"""
        import time
        
        processor = DataProcessor()
        
        # Crea dataset grande
        dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
        large_history = pd.DataFrame({
            'Open': 100 + np.cumsum(np.random.randn(len(dates)) * 0.5),
            'High': 105 + np.cumsum(np.random.randn(len(dates)) * 0.5),
            'Low': 95 + np.cumsum(np.random.randn(len(dates)) * 0.5),
            'Close': 100 + np.cumsum(np.random.randn(len(dates)) * 0.5),
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)
        
        # Assicura logica dei prezzi
        large_history['High'] = large_history[['Open', 'Close', 'High']].max(axis=1)
        large_history['Low'] = large_history[['Open', 'Close', 'Low']].min(axis=1)
        
        start_time = time.time()
        indicators = processor._calculate_technical_indicators(large_history)
        processing_time = time.time() - start_time
        
        # Elaborazione dovrebbe completarsi in tempo ragionevole (< 5 secondi)
        self.assertLess(processing_time, 5.0)
        self.assertIsInstance(indicators, dict)
        self.assertGreater(len(indicators), 0)

def run_all_tests():
    """Esegue tutti i test"""
    # Crea test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Aggiungi tutte le classi di test
    test_classes = [
        TestYFinanceClient,
        TestDataProcessor,
        TestHelpers,
        TestIntegration,
        TestErrorHandling,
        TestPerformance
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Esegui i test
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    print("🧪 Eseguendo test suite completa...\n")
    
    success = run_all_tests()
    
    if success:
        print("\n✅ Tutti i test sono passati!")
    else:
        print("\n❌ Alcuni test sono falliti.")
        sys.exit(1)
