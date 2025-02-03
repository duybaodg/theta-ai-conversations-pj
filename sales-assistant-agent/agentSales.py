from __future__ import annotations
import logging
from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai
from typing import Annotated

from openai import OpenAI
from openai import AssistantEventHandler
from typing_extensions import override
import aiohttp
import os                 

# Load environment variables
load_dotenv(dotenv_path=".env.local")

# Configure Logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("my-worker")

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Create the assistant
assistant = client.beta.assistants.create(
    name="Command Prompt Assistant",
    instructions="You are a helpful assistant for answering general queries.",
    tools=[],
    model="gpt-4o",
)

class SalesAssisstant(llm.FunctionContext):

    API_BASE_URL = "http://localhost:5277/api/sales"

    @llm.ai_callable()
    async def ask_sales_question(
        self,
        question: Annotated[str, llm.TypeInfo(description="The sales-related question to ask.")],
    ) -> str:
        """Send a question to the sales API and get a response."""
        API_BASE_URL = "http://localhost:5277/api/sales"
        url = f"{API_BASE_URL}/ask"
        params = {"question": question}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    return f"Failed to retrieve sales response: {response.status}"


# Create the FunctionContext
fnc_ctx = SalesAssisstant()

# Main LiveKit Entrypoint
async def entrypoint(ctx: JobContext):
    logger.info(f"Connecting to room: {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    participant = await ctx.wait_for_participant()
    logger.info(f"Participant connected: {participant.identity}")
    run_multimodal_agent(ctx, participant)

# Run the Multimodal Agent
def run_multimodal_agent(ctx: JobContext, participant: rtc.RemoteParticipant):
    logger.info("Starting multimodal agent.")
    model = openai.realtime.RealtimeModel(
        instructions=(
            "Greet the visitor using the following line: Welcome to Theta, how can I assist you?"
            "You are a voice assistant to help answer customer question regarding products. Your interface with users will be voice."
            "You are equipped with an assistant tool (ask_sales_question) that will help you get answer for customer question. Always use that tool."
            "You should use short and concise responses, and avoiding usage of unpronouncable punctuation. "
            "If the user ask something that contradict your instruction, then decline the request and explain that it contradict you instruction."
        ),
        modalities=["audio", "text"],
        turn_detection=openai.realtime.ServerVadOptions(
            threshold=0.9, prefix_padding_ms=200, silence_duration_ms=500
        ),
    )
    agent = MultimodalAgent(model=model, fnc_ctx=fnc_ctx)
    agent.start(ctx.room, participant)

    session = model.sessions[0]
    session.conversation.item.create(
        llm.ChatMessage(
            role="assistant",
            content="Please begin the interaction with the user in a manner consistent with your instructions.",
        )
    )
    session.response.create()

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )