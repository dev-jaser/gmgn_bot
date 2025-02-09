import asyncio
import logging
from core.data_engine import GmgnDataEngine
from core.pattern_matcher import AlphaPatternMatcher
from core.trading_executor import ExecutionEngine
from config import Config


class TradingBot:
    """Institutional trading system orchestrator"""

    def __init__(self):
        logging.basicConfig(
            filename=Config.LOGS_DIR / 'bot.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        self.data_engine = GmgnDataEngine()
        self.pattern_matcher = AlphaPatternMatcher()
        self.execution_engine = ExecutionEngine()

    async def run(self):
        """Professional trading loop"""
        while True:
            try:
                await self.data_engine.ingest_stream()
            except Exception as e:
                logging.error(f"Critical failure: {e}")
                await asyncio.sleep(30)


if __name__ == "__main__":
    bot = TradingBot()
    asyncio.run(bot.run())
