#!/usr/bin/python3
import os
import json
import requests
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from typing import List
from uagents import Agent, Context, Model

# Load environment variables
load_dotenv()
ANALYST_AGENT_ADDRESS = os.getenv("ANALYST_AGENT_ADDRESS")
COLLECTOR_AGENT_SEED = os.getenv("COLLECTOR_AGENT_SEED")
COLLECTOR_OUTPUT_FILE = os.getenv("COLLECTOR_OUTPUT_FILE", "sent_to_analyst.json")

if not ANALYST_AGENT_ADDRESS:
    print("❌ ANALYST_AGENT_ADDRESS not found in .env")
    exit(1)

# Data model
class CandlesPayload(Model):
    data: List[dict]

# Initialize agent
collector = Agent(
    name="collector_agent",
    seed=COLLECTOR_AGENT_SEED,
    port=5051,
    endpoint=["http://127.0.0.1:5051/submit"]
)

# Interactive user command loop
async def command_loop(ctx: Context):
    while True:
        try:
            choice = input("\n🟡 Enter a command (1 — collect, 2 — exit):\n> ").strip()
            if choice == "1":
                await collect_data(ctx)
            elif choice == "2":
                print("👋 Exiting. See you next time!")
                os._exit(0)
            else:
                print("⚠️ Please enter 1 or 2.")
        except KeyboardInterrupt:
            print("\n👋 Stopped with Ctrl+C")
            os._exit(0)

# Data collection from Binance
async def collect_data(ctx: Context):
    ctx.logger.info("📊 Collecting 4h BTC/USDT candles from Binance (approx. 90 days)...")

    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": "BTCUSDT", "interval": "4h", "limit": 1500}

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        ctx.logger.error(f"❌ Request error: {e}")
        return

    candles = [
        {
            "time": datetime.utcfromtimestamp(k[0] / 1000).isoformat(),
            "open": k[1],
            "high": k[2],
            "low":  k[3],
            "close": k[4],
            "volume": k[5]
        } for k in data
    ]

    ctx.logger.info(f"✅ Fetched {len(candles)} candles")

    try:
        with open(COLLECTOR_OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(candles, f, ensure_ascii=False, indent=2)
        ctx.logger.info(f"📝 Data saved to {COLLECTOR_OUTPUT_FILE}")
    except Exception as e:
        ctx.logger.error(f"❌ Failed to save data: {e}")

    await ctx.send(ANALYST_AGENT_ADDRESS, CandlesPayload(data=candles))
    ctx.logger.info(f"📤 Sent to analyst agent: {ANALYST_AGENT_ADDRESS}")
    print("✅ Done. You can run command 1 again or 2 to exit.")

# Startup greeting
@collector.on_event("startup")
async def ask_user(ctx: Context):
    print("\n🔹 Welcome to Collector Agent")
    print("This agent collects 4-hour BTC/USDT candles from Binance and sends them to the analyst agent.")
    print("\n📋 Available commands:")
    print("  1 — 📥 Collect and send data")
    print("  2 — ❌ Exit\n")
    ctx.logger.info("⌨️  Waiting for user input...")
    asyncio.create_task(command_loop(ctx))

if __name__ == "__main__":
    collector.run()

