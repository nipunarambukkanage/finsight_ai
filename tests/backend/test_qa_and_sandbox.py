import pytest
import pandas as pd
import numpy as np
from backend.app.strategy.sandbox import strategy_sandbox
from backend.app.strategy.qa_agent import qa_agent
from backend.app.orchestration.contracts import ImplementationOutput

def test_ast_sandbox_blocks_forbidden_imports():
    """Verify AST check rejects forbidden system and network modules."""
    malicious_codes = [
        "import os\nprint(os.environ)",
        "import subprocess\nsubprocess.run(['dir'])",
        "import socket\ns = socket.socket()",
        "import requests\nr = requests.get('https://google.com')",
        "eval('1 + 1')",
        "f = open('secrets.txt', 'r')"
    ]
    for code in malicious_codes:
        passed, errors = strategy_sandbox.static_ast_check(code)
        assert passed is False, f"Code should have been blocked: {code}"
        assert len(errors) > 0

def test_ast_sandbox_allows_whitelisted_imports():
    """Verify AST check permits approved numerical and mathematical modules."""
    safe_code = (
        "import numpy as np\n"
        "import pandas as pd\n"
        "import math\n"
        "from typing import List\n\n"
        "class MyStrategy:\n"
        "    pass\n"
    )
    passed, errors = strategy_sandbox.static_ast_check(safe_code)
    assert passed is True
    assert len(errors) == 0

def test_qa_agent_detects_lookahead_bias():
    """Verify QA Agent catches cheating strategies that access future prices."""
    cheating_code = (
        "import numpy as np\n"
        "import pandas as pd\n\n"
        "class CandidateStrategy:\n"
        "    def generate_signals(self, df: pd.DataFrame) -> np.ndarray:\n"
        "        # CHEATING: Look at future price using shift(-1)\n"
        "        future_ret = df['close'].shift(-5) - df['close']\n"
        "        signals = np.where(future_ret > 0, 1, 0)\n"
        "        return signals\n"
    )
    impl = ImplementationOutput(
        strategy_id="strat-cheater",
        source_code=cheating_code,
        test_code="print('UNIT_TESTS_PASSED')",
        review_status="pending_qa"
    )
    prices = [100.0 + i for i in range(50)]
    sample_df = pd.DataFrame({"close": prices})

    res = qa_agent.evaluate_implementation(impl, sample_df)
    assert res.lookahead_passed is False
    assert res.passed is False
    assert any("Look-Ahead Bias" in d for d in res.details)

def test_qa_agent_passes_valid_strategy():
    """Verify QA Agent passes valid non-anticipative momentum strategy."""
    valid_code = (
        "import numpy as np\n"
        "import pandas as pd\n\n"
        "class CandidateStrategy:\n"
        "    def generate_signals(self, df: pd.DataFrame) -> np.ndarray:\n"
        "        close = df['close']\n"
        "        sma = close.rolling(10, min_periods=10).mean()\n"
        "        return (close > sma).fillna(0).astype(int).values\n"
    )
    test_code = (
        "import numpy as np\n"
        "import pandas as pd\n"
        "from candidate import CandidateStrategy\n"
        "df = pd.DataFrame({'close': range(50)})\n"
        "strat = CandidateStrategy()\n"
        "sigs = strat.generate_signals(df)\n"
        "assert len(sigs) == 50\n"
        "print('UNIT_TESTS_PASSED')\n"
    )
    impl = ImplementationOutput(
        strategy_id="strat-valid",
        source_code=valid_code,
        test_code=test_code,
        review_status="pending_qa"
    )
    prices = [100.0 + i for i in range(50)]
    sample_df = pd.DataFrame({"close": prices})

    res = qa_agent.evaluate_implementation(impl, sample_df)
    assert res.passed is True
    assert res.ast_valid is True
    assert res.unit_tests_passed is True
    assert res.invariants_passed is True
    assert res.lookahead_passed is True
