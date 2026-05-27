#!/usr/bin/env python3
"""
TradeFlow - AI Agent Orchestrated Trading Pipeline
UiPath AgentHack 2026 - Track 1: Maestro Case

Architecture:
  LangChain Agents → UiPath Orchestrator → Binance Execution
  Human-in-the-loop for risk approval
"""
import json, time, requests, os
from datetime import datetime
from typing import Optional

# ====== Market Data Agent ======
class MarketAgent:
    """Fetches real-time market data from Binance"""
    def __init__(self):
        self.base = "https://api.binance.com/api/v3"
    
    def get_price(self, symbol: str) -> float:
        try:
            r = requests.get(f"{self.base}/ticker/price?symbol={symbol}USDT", timeout=5)
            return float(r.json()["price"])
        except: return 0
    
    def get_klines(self, symbol: str, interval="1h", limit=100):
        try:
            r = requests.get(f"{self.base}/klines",
                params={"symbol": f"{symbol}USDT", "interval": interval, "limit": limit}, timeout=10)
            return [float(d[4]) for d in r.json()]
        except: return []
    
    def scan(self) -> dict:
        pairs = ["BTC", "ETH", "BNB", "SOL"]
        data = {}
        for s in pairs:
            prices = self.get_klines(s)
            if prices:
                data[s] = {
                    "price": self.get_price(s),
                    "change_1h": (prices[-1] - prices[-2]) / prices[-2] * 100 if len(prices) > 2 else 0,
                    "change_24h": (prices[-1] - prices[-25]) / prices[-25] * 100 if len(prices) > 25 else 0,
                }
        return data

# ====== Analysis Agent ======
class AnalysisAgent:
    """Analyzes market data and generates trading signals"""
    
    def __init__(self):
        self.agent_id = "tradeflow-analysis-v1"
        self.signals = []
    
    def compute_rsi(self, prices, period=14):
        if len(prices) < period+1: return 50
        import numpy as np
        deltas = np.diff(prices[-period-1:])
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:]) if np.mean(losses[-period:]) > 0 else 1
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def analyze(self, market_data: dict) -> dict:
        signals = {}
        for sym, data in market_data.items():
            price = data["price"]
            ch1 = data["change_1h"]
            ch24 = data["change_24h"]
            
            score = 0
            reasons = []
            
            if ch1 < -2: score += 2; reasons.append("Oversold 1h")
            elif ch1 > 2: score -= 2; reasons.append("Overbought 1h")
            
            if ch24 < -5: score += 1; reasons.append("Dip -24h")
            
            if score >= 2:
                signal = "BUY"
            elif score <= -2:
                signal = "SELL"
            else:
                signal = "HOLD"
            
            signals[sym] = {
                "price": price,
                "signal": signal,
                "score": score,
                "confidence": min(abs(score)/4.0, 0.9),
                "reasons": reasons,
                "timestamp": datetime.now().isoformat()
            }
        return signals

# ====== Risk Agent ======
class RiskAgent:
    """Risk management - human-in-the-loop checkpoint"""
    
    def __init__(self, max_position_pct=0.1, max_drawdown_pct=0.05):
        self.max_position = max_position_pct
        self.max_drawdown = max_drawdown_pct
        self.positions = {}
        self.pending_approvals = []
    
    def evaluate(self, trade: dict, portfolio_value: float) -> str:
        """APPROVED / DENIED / REVIEW"""
        if trade["confidence"] < 0.5:
            return "DENIED"
        
        position_pct = trade.get("amount", 0) / portfolio_value if portfolio_value > 0 else 0
        if position_pct > self.max_position:
            return "REVIEW"  # Needs human approval
        
        return "APPROVED"
    
    def request_human_approval(self, trade: dict):
        """Creates a human-in-the-loop approval request"""
        approval = {
            "trade": trade,
            "status": "PENDING",
            "created": datetime.now().isoformat(),
            "approval_id": f"APR-{int(time.time())}"
        }
        self.pending_approvals.append(approval)
        return approval

# ====== Execution Agent ======
class ExecutionAgent:
    """Executes approved trades via Binance API"""
    
    def __init__(self, api_key="", api_secret=""):
        self.api_key = api_key
        self.api_secret = api_secret
        self.executed = []
    
    def execute(self, trade: dict) -> dict:
        """Execute a trade (simulated for hackathon)"""
        result = {
            "trade": trade,
            "status": "EXECUTED" if trade.get("approved") else "REJECTED",
            "timestamp": datetime.now().isoformat(),
            "execution_id": f"EXEC-{int(time.time())}"
        }
        self.executed.append(result)
        return result

# ====== UiPath Orchestrator Interface ======
class TradeFlowOrchestrator:
    """Main orchestrator - the UiPath Maestro Case equivalent"""
    
    def __init__(self):
        self.market = MarketAgent()
        self.analysis = AnalysisAgent()
        self.risk = RiskAgent()
        self.execution = ExecutionAgent()
        self.portfolio = 5000  # Starting capital
        self.cases = []
    
    def run_pipeline(self):
        """Execute one full trading pipeline cycle"""
        case_id = f"CASE-{int(time.time())}"
        case = {
            "case_id": case_id,
            "started": datetime.now().isoformat(),
            "stages": []
        }
        
        # Stage 1: Intake - Market Data
        market_data = self.market.scan()
        case["stages"].append({"stage": "INTAKE", "status": "COMPLETE", "data": market_data})
        
        # Stage 2: Analysis - AI Signals
        signals = self.analysis.analyze(market_data)
        case["stages"].append({"stage": "ANALYSIS", "status": "COMPLETE", "signals": signals})
        
        # Stage 3: Decision - Risk Check + Human Approval
        trades = []
        for sym, sig in signals.items():
            if sig["signal"] in ("BUY", "SELL"):
                trade = {
                    "symbol": sym,
                    "signal": sig["signal"],
                    "price": sig["price"],
                    "confidence": sig["confidence"],
                    "amount": self.portfolio * 0.05  # 5% position
                }
                decision = self.risk.evaluate(trade, self.portfolio)
                trade["risk_decision"] = decision
                
                if decision == "REVIEW":
                    approval = self.risk.request_human_approval(trade)
                    trade["approval"] = approval
                elif decision == "APPROVED":
                    trade["approved"] = True
                
                trades.append(trade)
        
        case["stages"].append({"stage": "DECISION", "status": "COMPLETE", "trades": trades})
        
        # Stage 4: Execution
        executed = []
        for trade in trades:
            if trade.get("approved"):
                result = self.execution.execute(trade)
                executed.append(result)
        
        case["stages"].append({"stage": "EXECUTION", "status": "COMPLETE", "executed": executed})
        
        # Stage 5: Settlement
        case["stages"].append({
            "stage": "SETTLEMENT",
            "status": "COMPLETE",
            "summary": f"{len(executed)} trades executed, {len([t for t in trades if t.get('risk_decision')=='REVIEW'])} pending review"
        })
        
        self.cases.append(case)
        return case
    
    def get_status(self) -> dict:
        return {
            "cases_completed": len(self.cases),
            "pending_approvals": len(self.risk.pending_approvals),
            "executed_trades": len(self.execution.executed),
            "portfolio": self.portfolio
        }

# ====== Demo ======
if __name__ == "__main__":
    orchestrator = TradeFlowOrchestrator()
    
    print("=" * 50)
    print("TradeFlow - UiPath AgentHack Demo")
    print("=" * 50)
    
    # Run pipeline
    case = orchestrator.run_pipeline()
    
    print(f"\nCase: {case['case_id']}")
    for stage in case["stages"]:
        print(f"  [{stage['stage']}] {stage['status']}")
    
    status = orchestrator.get_status()
    print(f"\nPipeline Status: {status}")
    
    # Save output
    with open("/home/administrator/hackathons/uipath/tradeflow_demo.json", "w") as f:
        json.dump(case, f, indent=2, default=str)
    
    print("\nPipeline output saved to tradeflow_demo.json")
