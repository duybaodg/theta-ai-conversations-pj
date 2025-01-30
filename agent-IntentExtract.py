from __future__ import annotations
import logging
import re
from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai
import aiohttp
from typing import Annotated
from word2number import w2n

load_dotenv(dotenv_path=".env.local")

API_BASE_URL = "https://ai-convo-api-a5fkhmf4huayhzcv.australiaeast-01.azurewebsites.net"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("my-worker")

class VisitorManagementTools(llm.FunctionContext):

    async def arrive_meeting(self, visitor_name: str, employee_name: str) -> str:
        """Register a visitor for a meeting."""
        url = f"{API_BASE_URL}/visitors/arrive-meeting"
        payload = {"visitorName": visitor_name, "meetingWith": employee_name}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return "The specified employee was not found. Please check the details and try again."
                else:
                    return f"Failed to register the meeting: {response.status}"

    async def arrive_courier(self, courier_name: str) -> str:
        """Register a courier arrival."""
        url = f"{API_BASE_URL}/visitors/arrive-courier"
        payload = {"CourierName": courier_name}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return f"Failed to register the courier: {response.status}"

    async def arrive_contractor(self, contractor_name: str, company_name: str) -> str:
        """Register a contractor arrival."""
        url = f"{API_BASE_URL}/visitors/arrive-contractor"
        payload = {"VisitorName": contractor_name, "Company": company_name}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return "The specified company was not found. Please check the details and try again."
                else:
                    return f"Failed to register the contractor: {response.status}"

    async def sign_out(self, visitor_id: int) -> str:
        """Sign out a visitor."""
        url = f"{API_BASE_URL}/visitors/sign-out"
        payload = {"VisitorId": visitor_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return f"Failed to sign out the visitor: {response.status}"

    async def general_enquiry(self) -> str:
        """Handle a general enquiry."""
        logger.info("Reception notified for a general enquiry.")
        return "Reception has been notified. Please wait for assistance."

    async def list_employees(self, pin: int) -> str:
        """List employees if the PIN is correct."""
        ADMIN_PIN = 987456
        if int(pin) != ADMIN_PIN:
            logger.debug(f"Invalid PIN entered: {pin}")
            return "Invalid PIN. Access denied."

        url = f"{API_BASE_URL}/employees"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    employees = await response.json()
                    employee_names = ', '.join([emp['name'] for emp in employees])
                    return f"Access granted. Employees: {employee_names}"
                elif response.status == 403:
                    return "Unauthorized access. Please check your credentials."
                else:
                    return f"Failed to retrieve employees: {response.status}"


def extract_intent(user_text: str) -> str:
    user_text = user_text.lower()
    if "meeting" in user_text or "here to see" in user_text:
        return "arrive_meeting"
    elif "courier" in user_text or "delivery" in user_text:
        return "arrive_courier"
    elif "contractor" in user_text:
        return "arrive_contractor"
    elif "sign out" in user_text:
        return "sign_out"
    elif "employee list" in user_text or "show employees" in user_text:
        return "list_employees" # Only ask for PIN here
    elif "help" in user_text or "reception" in user_text:
        return "general_enquiry"
    else:
        return "unknown"


def extract_visitor_name(user_text: str) -> str | None:
    match = re.search(r"(?:visitor\s|name is\s)([a-zA-Z\s]+)", user_text, re.IGNORECASE)
    return match.group(1).strip() if match else None

def extract_employee_name(user_text: str) -> str | None:
    match = re.search(r"(?:with\s|to meet\s|meeting with\s)([a-zA-Z\s]+)", user_text, re.IGNORECASE)
    return match.group(1).strip() if match else None

def extract_pin(user_text: str) -> int | None:
    match = re.search(r"\b(\d[\d\s]*)\b", user_text)
    if match:
        pin = match.group(1).replace(" ", "")
        return int(pin) if pin.isdigit() else None
    try:
        return w2n.word_to_num(user_text)
    except ValueError:
        return None


async def handle_user_input(user_text: str):
    intent = extract_intent(user_text)

    if intent == "arrive_meeting":
        visitor_name = extract_visitor_name(user_text)
        employee_name = extract_employee_name(user_text)
        if not visitor_name:
            return "Who is the visitor?"
        if not employee_name:
            return "Who are you meeting with?"
        return await fnc_ctx.arrive_meeting(visitor_name, employee_name)

    elif intent == "list_employees":
        pin = extract_pin(user_text)
        if not pin:
            return "Please provide your PIN to access the employee list."
        return await fnc_ctx.list_employees(pin)

    else:
        return await fnc_ctx.general_enquiry()


# def run_multimodal_agent(ctx: JobContext, participant: rtc.RemoteParticipant):
#     model = openai.realtime.RealtimeModel(modalities=["audio", "text"])

#     agent = MultimodalAgent(model=model, fnc_ctx=fnc_ctx)
#     agent.start(ctx.room, participant)

#     session = model.sessions[0]

#     @session.on_message
#     async def process_transcribed_text(msg: llm.ChatMessage):
#         if msg.role == "user":
#             user_text = msg.content
#             response = await handle_user_input(user_text)
#             session.response.create(content=response)

def run_multimodal_agent(ctx: JobContext, participant: rtc.RemoteParticipant):
    logger.info("Starting multimodal agent.")
    model = openai.realtime.RealtimeModel(
        instructions=(
            "You are a voice assistant for visitor management. You can help with tasks such as registering visitors, "
            "couriers, and contractors, signing visitors out, and notifying reception of general enquiries, "
        ),
        modalities=["audio", "text"],
        turn_detection=openai.realtime.ServerVadOptions(
            threshold=0.95, prefix_padding_ms=200, silence_duration_ms=500
        ),
    )
    agent = MultimodalAgent(model=model, fnc_ctx=fnc_ctx)
    agent.start(ctx.room, participant)

    session = model.sessions[0]
    session.conversation.item.create(
        llm.ChatMessage(
            role="assistant",
            content="Welcome! How can I assist you today?",
        )
    )
    session.response.create()


fnc_ctx = VisitorManagementTools()

async def entrypoint(ctx: JobContext):
    logger.info(f"Connecting to room: {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    participant = await ctx.wait_for_participant()
    logger.info(f"Participant connected: {participant.identity}")
    run_multimodal_agent(ctx, participant)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))