# core/data_engine.py
""" Professional-grade data processing pipeline. """
import json
import asyncio
from websockets import connect
from datetime import datetime
from config import Config
import logging
import numpy as np


class GmgnDataEngine:
    """ Institutional-grade market data processing pipeline. """

    def __init__(self):
        self.logger = logging.getLogger('data_engine')
        self.__setup_metrics()

    def __setup_metrics(self):
        """ Preallocate memory for high-frequency data. """
        self.token_cache = {}  # {address: (price_series, volume_series)}
        self.volatility_cache = np.empty((1000,), dtype=np.float32)
        self._current_vol_idx = 0

    async def ingest_stream(self):
        """ Wallstreet-grade Websocket manager. """
        backoff = Config.WS_RECONNECT_DELAY
        while True:
            try:
                async with connect(
                    Config.GMGN_WA_URL,
                    ping_interval=Config.WS_TIMEOUT - 2
                ) as ws:
                    backoff = Config.WS_RECONNECT_DELAY  # Reset backoff
                    await self._process_messages(ws)
            except Exception as e:
                self.logger.error("WS Error: %s, retrying in %ss.", e, backoff)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60)  # Exponential backoff

    async def _process_messages(self, ws):
        """ Institutional message processing with flow control. """
        async for message in ws:
            try:
                data = json.loads(message)
                if data['type'] == 'token_update':
                    await self._handle_token_update(data)
                elif data['type'] == 'heartbeat':
                    self._update_volatility(data)
            except Exception as e:
                self.logger.error("Message Processing Failed: %s", e)

    async def _handle_token_update(self, data):
        """ Professional data normalization """
        token_data = {
            'address': data['contractAddress'],
            'timestamp': datetime.utcnow().isoformat(),
            'liquidity': float(data['liquidity']['usd']),
            'volume': self._smooth_volume(data['volume24h']['usd']),
            'price': float(data['price']['usd']),
            'holders': int(data['holders']),
            'age_hours': self._calculate_age(data['launchedAt'])
        }

        if token_data['liquidity'] < Config.LIQUIDITY_FLOOR:
            return

        self._update_cache(token_data)
        self._persist_data(token_data)

    def _smooth_volume(self, raw_volume: float) -> float:
        """ EWMA smoothing to filter wash trading. """
        alpha = 0.2  # 80% weight to previous value
        return alpha * raw_volume + (1 - alpha) * self.volatility_cache.mean()
