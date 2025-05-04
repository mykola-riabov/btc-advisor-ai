#!/usr/bin/python3
import os
import requests
from dotenv import load_dotenv
from uagents import Agent, Context, Model

# Load environment variables
load_dotenv()
ASI_API_KEY = os.getenv("ASI_API_KEY")
ASI_API_URL = "https://api.asi1.ai/v1/chat/completions"
OUTPUT_FILE = os.getenv("ADVISOR_OUTPUT_FILE", "advisor_output.txt")

if not ASI_API_KEY:
    print("❌ Missing ASI_API_KEY in .env")
    exit(1)

# Define expected message structure
class AnalysisResult(Model):
    summary: dict

# Initialize agent
advisor = Agent(
    name="advisor_agent",
    seed=os.getenv("ADVISOR_AGENT_SEED"),
    port=5053,
    endpoint=["http://127.0.0.1:5053/submit"]
)

# Message handler
@advisor.on_message(model=AnalysisResult)
async def handle_analysis(ctx: Context, sender: str, msg: AnalysisResult):
    summary = msg.summary
    latest_time = summary.get("latest_time", "unknown")
    last_close = summary.get("last_close", 0)

    # Prompt construction for LLM (in English)
    prompt = (
        f"You are a professional crypto trader.\n"
        f"Based on the following BTC/USDT data, write a professional market analysis and provide a 3-day forecast.\n\n"
        f"📅 Last candle: {latest_time}\n"
        f"📈 Last close: {last_close}\n\n"
        f"📊 Moving averages:\n"
        f" - SMA-14: {summary['sma_14']}\n"
        f" - SMA-20: {summary['sma_20']}\n"
        f" - SMA-50: {summary['sma_50']}\n"
        f" - SMA-100: {summary['sma_100']}\n\n"
        f"📉 7-day price range:\n"
        f" - Max: {summary['price_range_7d']['max']} ({summary['price_range_7d']['max_time']})\n"
        f" - Min: {summary['price_range_7d']['min']} ({summary['price_range_7d']['min_time']})\n\n"
        f"📊 14-day average volume: {summary['avg_volume_14d']}\n"
        f"🔥 Top volume candles:\n" +
        "\n".join([f" - {v['volume']} BTC at {v['time']}" for v in summary["top_volumes"]]) +
        "\n\n🕒 Recent 4H candles:\n" +
        "\n".join([
            f"{x['time']} O:{x['open']} H:{x['high']} L:{x['low']} C:{x['close']} V:{x['volume']}"
            for x in summary["raw_data_14d"][-12:]
        ]) +
        "\n\nPlease include:\n"
        "- Market summary\n"
        "- Key support/resistance levels\n"
        "- Volatility and trading activity\n"
        "- Forecast for the next 3 days\n"
        "- Recommendations for traders (long/short/stop-loss)\n"
        "Language: English. Style: Professional trader tone."
    )

    headers = {
        "Authorization": f"Bearer {ASI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "asi1-mini",
        "messages": [
            { "role": "system", "content": "You are a professional crypto trader." },
            { "role": "user", "content": prompt }
        ]
    }

    try:
        ctx.logger.info("🟢 Press Ctrl+C anytime to stop the agent.")
        ctx.logger.info("⏳ Advisor is analyzing the data. Please wait up to 30 seconds...")

        res = requests.post(ASI_API_URL, headers=headers, json=payload)
        res.raise_for_status()
        result = res.json()

        if "choices" in result and result["choices"]:
            text = result["choices"][0]["message"]["content"]
            print("\n📬 Advisor response:\n")
            print(text)

            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write(text)
            ctx.logger.info(f"📝 Response saved to {OUTPUT_FILE}")
        else:
            print("⚠️ Empty response from ASI-1 Mini.")
    except Exception as e:
        print(f"❌ Error while contacting ASI-1: {e}")

if __name__ == "__main__":
    advisor.run()

