# core/data_engine.py
""" Alpha Pattern Matcher Module. """
import numpy as np
import pandas as pd
from sklearn.neighbors import LocalOutlierFactor
from config import Config
from datetime import datetime


class AlphaPatternMatcher:
    """ Institutional-grade pattern recognition engine. """

    def __init__(self):
        self.model = LocalOutlierFactor(
            n_neighbors=Config.MODEL_PARAMS['n_neighbors'],
            metric=Config.MODEL_PARAMS['metric'],
            novelty=True,
            contamination=Config.MODEL_PARAMS['contamination']
        )
        self.feature_matrix = None
        self._load_historical_patterns()

    def _load_historical_patterns(self):
        """ Load successful patterns from DB """
        with Config.db_connection(Config.PATTERN_DB) as conn:
            df = pd.read_sql(
                "SELECT features, profitability FROM patterns"
                "WHERE created_at > DATE('now', '-30 days')",
                conn
            )
        if not df.empty:
            self.feature_matrix = np.stack(
                df['features'].apply(np.frombuffer)
            )
            self._train_model()

        def _train_model(self):
            """ Wallstreet grade model training. """
            scaled_features = self._scale_features(self.feature_matrix)
            self.model.fit(scaled_features)

        def _scale_features(self, data: np.ndarray) -> np.ndarray:
            """ Robust scaling for financial data. """
            median = np.median(data, axis=0)
            iqr = np.subtract(*np.percentile(data, [75, 25], axis=0))
            return (data - median) / (iqr + 1e-8)

    def _analyze_token(self, token_data: dict) -> float:
        """ Generate alpha signal score. """
        features = self._extract_features(token_data)
        if features is None:
            return 0.0

        scaled = self._scale_features(features.reshape(1, -1))
        return self.model.decision_function(scaled)[0]

    def _extract_features(self, data: dict) -> np.ndarray | None:
        """ Professional Feature Engineering. """
        try:
            return np.array([
                # Liquidity velocity (6h change)
                data['liquidity'] /
                self._get_historical_value(data['address'], 'liquidity'),
                # Volume acceleration (2nd derivative)
                data['volume'] - 2 *
                self._get_historical_value(data['address'], 'volume'),
                # Holder growth rate
                data['holders'] /
                (self._get_historical_value(data['address'], 'holders') + 1),
                # Price-volatility ratio
                data['price'] / (self._get_volatility() + 1e-6)
            ], dtype=np.float32)
        except KeyError:
            return None
