"""
FinSight AI - Developer Agent
Translates structured StrategySpecification into candidate Python strategy code.
"""

from typing import Dict, Any, Optional
from backend.app.orchestration.contracts import StrategySpecification, ImplementationOutput

class DeveloperAgent:
    """Autonomous agent responsible for writing deterministic candidate Python strategy code."""

    @staticmethod
    def generate_candidate_code(spec: StrategySpecification) -> ImplementationOutput:
        """
        Synthesizes candidate strategy class implementing generate_signals(df).
        Follows strict template without forbidden dependencies.
        """
        hypo = spec.hypothesis.lower()
        strategy_id = spec.strategy_id
        version = spec.version


        if "mean reversion" in hypo or "rsi" in hypo:
            source_code = (
                "import numpy as np\n"
                "import pandas as pd\n\n"
                "class CandidateStrategy:\n"
                "    \"\"\"\n"
                "    Mean Reversion RSI Strategy\n"
                "    \"\"\"\n"
                "    def __init__(self, rsi_period: int = 14, oversold: float = 30.0, overbought: float = 70.0):\n"
                "        self.rsi_period = rsi_period\n"
                "        self.oversold = oversold\n"
                "        self.overbought = overbought\n\n"
                "    def generate_signals(self, df: pd.DataFrame) -> np.ndarray:\n"
                "        close = df['close'].values\n"
                "        n = len(close)\n"
                "        signals = np.zeros(n, dtype=np.int32)\n"
                "        if n <= self.rsi_period:\n"
                "            return signals\n\n"
                "        diff = np.diff(close)\n"
                "        gains = np.maximum(diff, 0.0)\n"
                "        losses = -np.minimum(diff, 0.0)\n\n"
                "        avg_gain = np.mean(gains[:self.rsi_period])\n"
                "        avg_loss = np.mean(losses[:self.rsi_period])\n\n"
                "        for i in range(self.rsi_period, n - 1):\n"
                "            avg_gain = (avg_gain * (self.rsi_period - 1) + gains[i-1]) / self.rsi_period\n"
                "            avg_loss = (avg_loss * (self.rsi_period - 1) + losses[i-1]) / self.rsi_period\n"
                "            rs = avg_gain / (avg_loss + 1e-9)\n"
                "            rsi = 100.0 - (100.0 / (1.0 + rs))\n\n"
                "            if rsi < self.oversold:\n"
                "                signals[i] = 1\n"
                "            elif rsi > self.overbought:\n"
                "                signals[i] = 0\n"
                "            else:\n"
                "                signals[i] = signals[i-1]\n"
                "        return signals\n"
            )
        else:

            source_code = (
                "import numpy as np\n"
                "import pandas as pd\n\n"
                "class CandidateStrategy:\n"
                "    \"\"\"\n"
                "    Trend Following Dual SMA Crossover Strategy\n"
                "    \"\"\"\n"
                "    def __init__(self, fast_window: int = 10, slow_window: int = 30):\n"
                "        self.fast_window = fast_window\n"
                "        self.slow_window = slow_window\n\n"
                "    def generate_signals(self, df: pd.DataFrame) -> np.ndarray:\n"
                "        close = df['close']\n"
                "        fast_ma = close.rolling(window=self.fast_window, min_periods=self.fast_window).mean()\n"
                "        slow_ma = close.rolling(window=self.slow_window, min_periods=self.slow_window).mean()\n\n"
                "        raw_signal = (fast_ma > slow_ma).astype(int)\n"
                "        signals = raw_signal.fillna(0).astype(int).values\n"
                "        return signals\n"
            )

        test_code = (
            "import numpy as np\n"
            "import pandas as pd\n"
            "from candidate import CandidateStrategy\n\n"
            "def test_strategy_execution():\n"
            "    prices = [100.0 + (i * 0.5) for i in range(50)]\n"
            "    df = pd.DataFrame({'close': prices})\n"
            "    strat = CandidateStrategy()\n"
            "    signals = strat.generate_signals(df)\n"
            "    assert len(signals) == len(prices), 'Signal length must match DataFrame'\n"
            "    assert set(np.unique(signals)).issubset({0, 1, -1}), 'Signals must be in {-1, 0, 1}'\n"
            "    print('UNIT_TESTS_PASSED')\n\n"
            "if __name__ == '__main__':\n"
            "    test_strategy_execution()\n"
        )

        return ImplementationOutput(
            strategy_id=strategy_id,
            version=version,
            source_code=source_code,
            test_code=test_code,
            dependencies=["numpy", "pandas"],
            static_check_result={},
            review_status="pending_qa"
        )

developer_agent = DeveloperAgent()
