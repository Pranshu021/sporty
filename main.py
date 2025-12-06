import asyncio
import logging
from dotenv import load_dotenv
from agents import Runner
from models.context import UserContext
from app_agents.manager import manager_agent

# ── -1. Logging Setup ──
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load environment variables from .env file
logging.info("Loading environment variables from .env file...")
load_dotenv()
logging.info("Environment variables loaded.")


async def main():
    logging.info("Starting the agent run...")
    # Define the leagues and tournaments you are interested in
    context = UserContext(
        leagues_and_tournaments=[
            "Premier League",
            "LaLiga",
            "UEFA Champions League",
            "Bundesliga",
        ]
    )

    # The input to the manager_agent doesn't matter as it will use the get_current_time tool
    result = await Runner.run(
        manager_agent, input="start", context=context, max_turns=15
    )
    logging.info(f"Run finished. Final output: {result.final_output}")
    print("Run finished. Final output:", result.final_output)


if __name__ == "__main__":
    import nest_asyncio

    nest_asyncio.apply()
    asyncio.run(main())
