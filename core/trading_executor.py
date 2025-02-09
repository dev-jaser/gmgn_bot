# core/trading_executor.py
""" Trading Execution Engine """
from config import Config
import logging
from typing import Optional


class ExecutionEngine:
    """Institutional trading execution system"""

    def __init__(self):
        self.logger = logging.getLogger('execution')
        self.daily_trades = 0
        self.position_book = {}

    def evaluate_trade(self, signal_score: float, token_data: dict) -> Optional[dict]:
        """ Professional Trade Qualification. """
        if not self._pre_trade_checks(signal_score, token_data):
            return None

        return self._build_order(token_data)

    def _pre_trade_checks(self, score: float, data: dict) -> bool:
        """ Wallstreet grade compliance check. """
        if (self.daily_trades >= Config.RISK_PARAMS['max_daily_trades'] or
            data['liquidity'] < Config.LIQUIDITY_FLOOR or
                score < Config.RISK_PARAMS['min_confidence']):
            return False

        return True

    def _build_order(self, data: dict) -> dict:
        """Professional order sizing"""
        position_size = self._calculate_size(data)
        return {
            'symbol': data['address'],
            'side': 'BUY',
            'type': 'LIMIT',  # Avoid slippage
            'price': data['price'] * 1.005,  # Top of book
            'amount': position_size,
            'stoploss': data['price'] * (1 - Config.RISK_PARAMS['stop_loss']),
            'take_profit': data['price'] * (1 + Config.RISK_PARAMS['take_profit'])
        }

    def _calculate_size(self, data: dict) -> float:
        """Kelly Criterion-based sizing"""
        volatility = abs(
            data['price'] / self._get_historical_price(data['address']))
        kelly_fraction = volatility / Config.RISK_PARAMS['take_profit']
        return min(kelly_fraction * Config.RISK_PARAMS['max_position'], 0.1)
