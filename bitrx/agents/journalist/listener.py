import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
from agents.journalist.event_client import subscribe
from agents.journalist.journalist_agent import JournalistAgent, JournalistConfig

load_dotenv()


async def handle_event(event, config):
    """Each event gets its own agent instance and runs independently."""
    print(f"\n{'='*60}")
    print(f"  NEW EVENT [seq={event.seq}] tag={event.tag}")
    print(f"  {event.text[:120]}...")
    print(f"{'='*60}\n")

    # Each event gets its own agent instance
    with JournalistAgent(config) as agent:
        agent.index_knowledge("agents/journalist/knowledge")
        print(" Journalist is investigating...\n")
        response = agent.chat(event.text)
        print(f"\n Agent: {response}\n")
        print("-" * 60)


async def main():
    print("=" * 60)
    print("  Journalist Agent — Event Listener")
    print("  Subscribing to: press events")
    print("=" * 60)

    config = JournalistConfig.from_env()

    if not config.gemini_api_key:
        print("\n ERROR: GEMINI_API_KEY not set in .env file")
        return

    print("\n Agent ready — waiting for press events...\n")

    async for event in subscribe("press"):
        # Fire and forget — each event runs concurrently
        asyncio.create_task(handle_event(event, config))


if __name__ == "__main__":
    asyncio.run(main())