from agents import Agent
from models.context import UserContext
from tools.utils import get_current_time
from app_agents.finders import match_schedule_finder, match_results_finder
from prompts.system_prompts import MANAGER_AGENT_INSTRUCTIONS

# Main agent to manage the workflow. Triggers the Manager Agent which then handles the handovers.
# The Boss, Gaffer XD
manager_agent = Agent[UserContext](
    name="manager_agent",
    instructions=MANAGER_AGENT_INSTRUCTIONS,
    model="gpt-4o-mini",
    tools=[get_current_time],
    handoffs=[match_schedule_finder, match_results_finder],
)
