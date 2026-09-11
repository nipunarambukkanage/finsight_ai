"""
FinSight AI - Simulation-Only Shadow Trading Service
CRITICAL SAFETY BOUNDARY:
- Runs in simulation mode ONLY.
- Zero connection to brokerages, exchange execution APIs, or financial accounts.
- Generates hypothetical orders, simulates realistic fills, tracks virtual P&L.
- Requires explicit human approval record prior to activation.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import math
from backend.app.orchestration.contracts import ShadowSimulationResult
from backend.app.analytics.engine import QuantitativeAnalyticsEngine
from backend.app.core.logging import logger

class ShadowTradingService:
    def __init__(self):
        self._simulations: Dict[str, Dict[str, Any]] = {}

    def start_simulation(
        self,
        strategy_id: str,
        ticker: str,
        initial_cash: float = 250_000.0,
        approved_by: Optional[str] = None
    ) -> ShadowSimulationResult:
        """
        Activates a simulation-only shadow session. Requires human operator approval.
        """
        if not approved_by:
            raise PermissionError("Shadow trading activation requires explicit human approval.")

        sim_id = f"sim-{uuid.uuid4().hex[:8]}"

        sim_state = {
            "simulation_id": sim_id,
            "strategy_id": strategy_id,
            "ticker": ticker.upper(),
            "status": "ACTIVE",
            "approved_by": approved_by,
            "virtual_cash": initial_cash,
            "virtual_shares": 0.0,
            "realized_pnl": 0.0,
            "unrealized_pnl": 0.0,
            "simulated_pnl": 0.0,
            "total_slippage": 0.0,
            "total_costs": 0.0,
            "orders": [],
            "fills": [],
            "initial_cash": initial_cash,
            "last_price": 0.0,
            "updated_at": datetime.now(timezone.utc)
        }

        self._simulations[sim_id] = sim_state
        logger.info(f"Activated Simulation-Only Shadow Session {sim_id} for strategy {strategy_id} ({ticker}) approved by {approved_by}")

        return self._build_result(sim_state)

    def pause_simulation(self, simulation_id: str) -> ShadowSimulationResult:
        sim = self._simulations.get(simulation_id)
        if not sim:
            raise ValueError(f"Simulation '{simulation_id}' not found.")
        sim["status"] = "PAUSED"
        sim["updated_at"] = datetime.now(timezone.utc)
        logger.info(f"Paused shadow trading simulation {simulation_id}")
        return self._build_result(sim)

    def resume_simulation(self, simulation_id: str) -> ShadowSimulationResult:
        sim = self._simulations.get(simulation_id)
        if not sim:
            raise ValueError(f"Simulation '{simulation_id}' not found.")
        sim["status"] = "ACTIVE"
        sim["updated_at"] = datetime.now(timezone.utc)
        logger.info(f"Resumed shadow trading simulation {simulation_id}")
        return self._build_result(sim)

    def process_market_tick(
        self,
        simulation_id: str,
        current_price: float,
        signal: int,
        slippage_bps: float = 3.0,
        cost_bps: float = 5.0
    ) -> ShadowSimulationResult:
        """
        Simulates an incoming market tick, generates hypothetical orders, and fills them with realistic slippage.
        """
        sim = self._simulations.get(simulation_id)
        if not sim or sim["status"] != "ACTIVE":
            return self._build_result(sim) if sim else None

        sim["last_price"] = current_price
        ticker = sim["ticker"]
        now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


        if signal > 0 and sim["virtual_shares"] == 0:
            target_alloc = sim["virtual_cash"] * 0.90
            fill_price = current_price * (1.0 + (slippage_bps / 10000.0))
            shares = math.floor(target_alloc / fill_price)

            if shares > 0:
                trade_val = shares * fill_price
                costs = QuantitativeAnalyticsEngine.calculate_transaction_costs(trade_val, cost_bps)
                slip = QuantitativeAnalyticsEngine.calculate_slippage(trade_val, slippage_bps)

                order_id = f"ORD-{len(sim['orders'])+1}"
                sim["orders"].append({
                    "order_id": order_id,
                    "ticker": ticker,
                    "side": "BUY",
                    "shares": shares,
                    "order_type": "MARKET",
                    "status": "FILLED",
                    "timestamp": now_ts
                })

                sim["fills"].append({
                    "fill_id": f"FILL-{len(sim['fills'])+1}",
                    "order_id": order_id,
                    "price": round(fill_price, 2),
                    "shares": shares,
                    "costs": round(costs, 2),
                    "slippage": round(slip, 2),
                    "timestamp": now_ts
                })

                sim["virtual_cash"] -= (trade_val + costs)
                sim["virtual_shares"] = shares
                sim["total_costs"] += costs
                sim["total_slippage"] += slip


        elif signal <= 0 and sim["virtual_shares"] > 0:
            shares = sim["virtual_shares"]
            fill_price = current_price * (1.0 - (slippage_bps / 10000.0))
            trade_val = shares * fill_price
            costs = QuantitativeAnalyticsEngine.calculate_transaction_costs(trade_val, cost_bps)
            slip = QuantitativeAnalyticsEngine.calculate_slippage(trade_val, slippage_bps)

            order_id = f"ORD-{len(sim['orders'])+1}"
            sim["orders"].append({
                "order_id": order_id,
                "ticker": ticker,
                "side": "SELL",
                "shares": shares,
                "order_type": "MARKET",
                "status": "FILLED",
                "timestamp": now_ts
            })

            sim["fills"].append({
                "fill_id": f"FILL-{len(sim['fills'])+1}",
                "order_id": order_id,
                "price": round(fill_price, 2),
                "shares": shares,
                "costs": round(costs, 2),
                "slippage": round(slip, 2),
                "timestamp": now_ts
            })

            sim["virtual_cash"] += (trade_val - costs)
            sim["virtual_shares"] = 0.0
            sim["total_costs"] += costs
            sim["total_slippage"] += slip


        pos_val = sim["virtual_shares"] * current_price
        total_equity = sim["virtual_cash"] + pos_val
        sim["unrealized_pnl"] = pos_val
        sim["simulated_pnl"] = total_equity - sim["initial_cash"]
        sim["updated_at"] = datetime.now(timezone.utc)

        return self._build_result(sim)

    def _build_result(self, sim: Dict[str, Any]) -> ShadowSimulationResult:
        pos_val = sim["virtual_shares"] * sim["last_price"]
        total_equity = sim["virtual_cash"] + pos_val
        exposure = pos_val / total_equity if total_equity > 0 else 0.0

        return ShadowSimulationResult(
            simulation_id=sim["simulation_id"],
            strategy_id=sim["strategy_id"],
            status=sim["status"],
            virtual_portfolio={
                "cash": round(sim["virtual_cash"], 2),
                "shares": sim["virtual_shares"],
                "position_value": round(pos_val, 2),
                "total_equity": round(total_equity, 2),
                "initial_cash": sim["initial_cash"]
            },
            hypothetical_orders=sim["orders"],
            simulated_fills=sim["fills"],
            slippage_incurred=round(sim["total_slippage"], 2),
            simulated_pnl=round(sim["simulated_pnl"], 2),
            current_exposure=round(exposure, 4),
            is_simulation_only=True,
            disclaimer="SIMULATION ONLY: No real orders executed or broker connections active."
        )

shadow_trading_service = ShadowTradingService()
