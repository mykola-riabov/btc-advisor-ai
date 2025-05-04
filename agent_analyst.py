#!/usr/bin/python3
import os
import json
from dotenv import load_dotenv
from typing import List
from uagents import Agent, Context, Model

# Load environment variables
load_dotenv()
ADVISOR_AGENT_ADDRESS = os.getenv("ADVISOR_AGENT_ADDRESS")
ANALYST_OUTPUT_FILE = os.getenv("ANALYST_OUTPUT_FILE", "sent_to_advisor.json")

if not ADVISOR_AGENT_ADDRESS:
    print("❌ ADVISOR_AGENT_ADDRESS not found in .env")
    exit(1)

# Data models
class CandlesPayload(Model):
    data: List[dict]

class AnalysisResult(Model):
    summary: dict

# Initialize the agent
analyst = Agent(
    name="analyst_agent",
    seed=os.getenv("ANALYST_AGENT_SEED"),
    port=5052,
    endpoint=["http://127.0.0.1:5052/submit"]
)

@analyst.on_message(model=CandlesPayload)
async def handle_candles(ctx: Context, sender: str, msg: CandlesPayload):
    ctx.logger.info("📥 Received data from collector agent.")
    candles = msg.data
    ctx.logger.info(f"🕒 Total candles: {len(candles)}")

    if len(candles) < 100:
        ctx.logger.error("⛔ Not enough data for analysis.")
        return

    closes = [float(c["close"]) for c in candles]
    latest_time = candles[-1]["time"]
    last_close = float(candles[-1]["close"])

    ctx.logger.info("🧮 Calculating global moving averages...")
    def sma(data, period):
        return sum(data[-period:]) / period

    sma_14 = sma(closes, 14)
    sma_20 = sma(closes, 20)
    sma_50 = sma(closes, 50)
    sma_100 = sma(closes, 100)

    # Per-candle SMA
    ctx.logger.info("📈 Calculating moving averages for each candle...")
    sma_data = []
    for i in range(len(closes)):
        row = {
            "time": candles[i]["time"],
            "close": round(closes[i], 2)
        }
        if i >= 13:
            row["sma_14"] = round(sum(closes[i-13:i+1]) / 14, 2)
        if i >= 19:
            row["sma_20"] = round(sum(closes[i-19:i+1]) / 20, 2)
        if i >= 49:
            row["sma_50"] = round(sum(closes[i-49:i+1]) / 50, 2)
        if i >= 99:
            row["sma_100"] = round(sum(closes[i-99:i+1]) / 100, 2)
        sma_data.append(row)

    ctx.logger.info("📊 Determining 7-day range and volume metrics...")
    raw_data_14d = candles[-84:]
    closes_7d = raw_data_14d[-42:]

    max_7d = max(closes_7d, key=lambda x: float(x["close"]))
    min_7d = min(closes_7d, key=lambda x: float(x["close"]))

    top_volumes = sorted(raw_data_14d, key=lambda x: float(x["volume"]), reverse=True)[:5]
    top_vols_out = [{"volume": float(v["volume"]), "time": v["time"]} for v in top_volumes]
    avg_volume_14d = sum(float(c["volume"]) for c in raw_data_14d) / len(raw_data_14d)

    summary = {
        "latest_time": latest_time,
        "last_close": round(last_close, 2),
        "sma_14": round(sma_14, 2),
        "sma_20": round(sma_20, 2),
        "sma_50": round(sma_50, 2),
        "sma_100": round(sma_100, 2),
        "price_range_7d": {
            "max": float(max_7d["close"]),
            "max_time": max_7d["time"],
            "min": float(min_7d["close"]),
            "min_time": min_7d["time"]
        },
        "avg_volume_14d": round(avg_volume_14d, 2),
        "top_volumes": top_vols_out,
        "raw_data_14d": raw_data_14d,
        "sma_data": sma_data
    }

    ctx.logger.info("✅ Analysis complete.")
    ctx.logger.info("📤 Sending analysis to advisor agent...")
    ctx.logger.info(f"📌 Advisor address: {ADVISOR_AGENT_ADDRESS}")
    ctx.logger.info(f"📁 Output file: {ANALYST_OUTPUT_FILE}")

    message = AnalysisResult(summary=summary)

    try:
        with open(ANALYST_OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(message.dict(), f, ensure_ascii=False, indent=2)
        ctx.logger.info(f"📝 Saved analysis to {ANALYST_OUTPUT_FILE}")
    except Exception as e:
        ctx.logger.error(f"❌ Failed to save analysis: {e}")

    try:
        await ctx.send(ADVISOR_AGENT_ADDRESS, message)
        ctx.logger.info("✅ Successfully sent to advisor.")
    except Exception as e:
        ctx.logger.error(f"❌ Failed to send to advisor: {e}")

if __name__ == "__main__":
    analyst.run()

