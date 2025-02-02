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
import os           

import pandas as pd
from sqlalchemy import create_engine

ENDPOINT="database-1.cjky6womijvh.us-east-1.rds.amazonaws.com"
PORT="5432"
USER="postgres"
PASSWORD="admin12345"
DBNAME=""

def LoadDataFromDatabase():
    try:
        conn = create_engine(f"postgresql://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DBNAME}")
        SQL_Query = pd.read_sql_query('''SELECT * FROM users''', conn)
        print(SQL_Query)
        return SQL_Query
    except Exception as e:
        print("Database connection failed due to {}".format(e))  

    

os.environ["OPENAI_API_KEY"] = "sk-svcacct-CgWgSOj2RTUOUHIOIZF2wAOFcNVR0r9IMHNppVUFI5LMfOPH9qIu3IV5ha1XovSWNqyno8ST3BlbkFJ7Bdh93_ZqTraoRPU3Tv-R0y7gjVcpZNEg45sOwz-i47FIkBhugYsRZ1G2Ml7Ana_bPtIMAA"
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

    ENDPOINT="database-1.cjky6womijvh.us-east-1.rds.amazonaws.com"
    PORT="5432"
    USER="postgres"
    PASSWORD="admin12345"
    DBNAME=""

    try:
        conn = create_engine(f"postgresql://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DBNAME}")
        SQL_Query = pd.read_sql_query('''SELECT * FROM products''', conn)
        print(SQL_Query)
        data_json = SQL_Query.to_json(orient='records')
    except Exception as e:
        print("Database connection failed due to {}".format(e))  

    @llm.ai_callable()
    async def query_data(
        self,
        question: Annotated[str, llm.TypeInfo(description="Customer inquiry.")],
    ) -> str:
        """Querry"""
        prompt = f"Based on the following relational data, answer the question:\n{self.data_json}\nQuestion: {question}"
        chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "you are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-4o",
        )
        return chat_completion.choices[0].message.content

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
            "You are a voice assistant to help answer customer question regarding Theta products. Your interface with users will be voice."
            "Any question that customer have, look for it inside Theta products database."
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