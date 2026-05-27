# TradeFlow - UiPath AgentHack Submission
## Track 1: UiPath Maestro Case

### What
AI-driven trading pipeline orchestrated through UiPath Maestro Case.
Python LangChain agents handle market analysis, risk assessment, and trade execution.
UiPath orchestrates the end-to-end flow with human-in-the-loop checkpoints.

### Architecture
Market Agent → Analysis Agent → Risk Agent → Execution Agent
     ↑                                                   ↓
  Binance API                                      Trade History
     ↑                                                   ↓
  UiPath Maestro Case (Orchestration + Human Approval)

### Tech Stack
- Python + LangChain
- UiPath Maestro Case API
- Binance API
- NumPy/Pandas

### Demo
Run: python3 tradeflow.py
Output: tradeflow_demo.json with full pipeline trace
