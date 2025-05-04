# BTC Advisor AI

**BTC Advisor AI** is an autonomous multi-agent system for analyzing the BTC/USDT market and generating 3-day forecasts using artificial intelligence.

---

## 🎯 Project Purpose

This project demonstrates a **practical use case of AI agents** built on the [`uAgents`](https://github.com/fetchai/uAgents) framework.

- **Two agents** (Collector and Analyst) are standard uAgents that handle data collection and indicator calculations.
- **One agent** (Advisor) is an **AI-powered agent**, using the ASI-1 Mini language model to generate forecasts.
- Although the entire logic could be implemented in a single AI agent, this project intentionally uses **three separate roles** to showcase modular architecture and allow flexible scaling or replacement.

---

## 📦 Components

System flow:

```
Collector Agent ──► Analyst Agent ──► Advisor Agent
(from Binance)       (SMA analysis)      (AI forecast via ASI)
```

📚 Learn more about the agent architecture:  
👉 [Fetch.ai Innovation Lab — Core Concepts](https://innovationlab.fetch.ai/resources/docs/concepts-ai-agents/foundation-core-concepts)

---

## 🚀 What the system does

- 🔄 Retrieves 4-hour BTC/USDT candles from Binance (~90 days).
- 📈 Calculates SMA (14, 20, 50, 100), 7-day price ranges, volumes, and top candles.
- 🧠 Generates a summary and sends it to the ASI-1 Mini language model.
- 📬 Produces a professional 3-day market forecast (in English).
- 💾 Saves the result to a file and prints it to the terminal.

---

## 🧠 About ASI-1 Mini

Forecasts are generated using the **ASI-1 Mini** language model, developed by [Fetch.ai](https://fetch.ai/).  
It is the world's first Web3-native large language model (LLM), optimized for agent-based workflows.  
API access is provided via: [https://asi1.ai/](https://asi1.ai/)

---

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mykola-riabov/btc-advisor-ai.git
   cd btc-advisor-ai
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example` and configure:
   - Your ASI API key (`ASI_API_KEY`);
   - Agent addresses and seeds;
   - Output file paths.

---

## ⚙️ Scripts

| Script               | Description |
|----------------------|-------------|
| `agent_collector.py` | Downloads 4H BTC/USDT candles from Binance and sends them to the Analyst agent. |
| `agent_analyst.py`   | Calculates SMA and volume metrics and forwards the analysis to the Advisor agent. |
| `agent_advisor.py`   | Builds a prompt and sends it to ASI-1 Mini to receive the market forecast. |

---

## ▶️ How to use

1. Start all **three agents** in separate terminals:
   ```bash
   python3 agent_advisor.py
   python3 agent_analyst.py
   python3 agent_collector.py
   ```

2. In `agent_collector.py`, choose:
   ```
   1 — 📥 Fetch and send data
   2 — ❌ Exit
   ```

3. Wait for the forecast to appear in the terminal and be saved to `advisor_output.txt`.

---

## 📁 Output Files

- `sent_to_analyst.json` — candles from Collector → Analyst.
- `sent_to_advisor.json` — summary from Analyst → Advisor.
- `advisor_output.txt` — forecast from ASI-1 Mini.

---

## 💡 Dependencies

- Python 3.8+
- `uAgents`, `requests`, `python-dotenv`

---

## 📌 Notes

- A valid `ASI_API_KEY` is required to query ASI-1 Mini.
- The modular agent architecture allows easy extension with additional agents (e.g., alerts, arbitrage, cross-market strategies).
- Agents run locally and communicate via HTTP ports using uAgents messaging.

---