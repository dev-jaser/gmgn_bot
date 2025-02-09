""" Configuration for the quant trading system. """
# config.py
from pathlib import Path
import sqlite3
from datetime import timedelta


class Config:
    """ Institutional-grade configuration for quant trading. """

    # --- Directory Structure ---
    BASE_DIR = Path(__file__).parent.resolve()
    DATA_DIR = BASE_DIR / 'data'
    LOGS_DIR = BASE_DIR / 'logs'

    # --- Database Configuration ---
    LIVE_DB = DATA_DIR / 'market_data.db'
    PATTERN_DB = DATA_DIR / 'pattern_data.db'
    DB_TIMEOUT = 5  # Lock timeout in seconds

    # --- WebSocket Parameters ---
    GMGN_WA_URL = 'waa://api.gmgn.ai/defi/ws/v2'
    WS_TIMEOUT = 10  # Timeout in seconds
    WS_RECONNECT_DELAY = 5  # Exceptional backoff base

    # --- Quant Model Parameters ---
    FEATURE_WINDOW = timedelta(hours=6)
    LIQUIDITY_FLOOR = 250_000  # Minimum liquidity for a trade / in USD
    VOUME_SPIKE_MULTIPLIER = 3.2
    RISK_PARAMS = {
        'max-position': 0.03,  # 3% of portfolio
        'stop_loss': 0.15,  # 15% trailing stop
        'take_profit': 2.5,  # 2.5:1 risk-reward ratio
        'max_daily_trades': 5
    }

    # --- Machine Learning ---
    MODEL_PARAMS = {
        'n_neighbors': 7,
        'metric': 'mahalanobis',
        'contamination': 0.01
    }

    @classmethod
    def db_connection(cls, db_path: Path) -> sqlite3.Connection:
        """ Institutional DB connection with WAL mode. """
        conn = sqlite3.connect(db_path, timeout=cls.DB_TIMEOUT)
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA synchronous=NORMAL')
        return conn
