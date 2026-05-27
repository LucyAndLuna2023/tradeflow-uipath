# UiPath AgentHack - AI驱动的交易自动化
# Track: UiPath Maestro Case
# 实现: Python LangChain Agents + UiPath Orchestrator

## 项目名: TradeFlow - AI Agent Orchestrated Trading Pipeline

## 思路
UiPath做编排层，LangChain/CrewAI Agent做执行层：
1. UiPath Orchestrator 管理交易流水线
2. Python Agent 执行市场扫描+信号生成
3. UiPath 处理异常+人工审批节点
4. 端到端自动化: 数据采集→分析→决策→执行→报告

## 技术栈
- UiPath Maestro Case (编排层)
- Python + LangChain/CrewAI (Agent层)
- Binance API (交易执行)
- Slack (通知+审批)

## 赛道: Track 1 - Maestro Case
Case场景: 量化交易流水线
- Intake: 市场数据采集
- Analysis: AI信号分析
- Decision: 风险审核(人工节点)
- Execution: 订单执行
- Settlement: 成交结算+报告

## 时间线 (34天)
- Week 1-2: UiPath平台学习 + LangChain Agent开发
- Week 3: 集成调试
- Week 4-5: Demo视频 + 提交

## 提交物
1. UiPath项目包
2. GitHub代码
3. Demo视频
4. 架构文档
