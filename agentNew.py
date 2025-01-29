from __future__ import annotations
import logging
from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai
import aiohttp
from typing import Annotated

# Load environment variables
load_dotenv(dotenv_path=".env.local")

# API Base URL
API_BASE_URL = "https://ai-convo-api.azurewebsites.net"

# Configure Logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("my-worker")

# Define a FunctionContext for Tools
class VisitorManagementTools(llm.FunctionContext):

    @llm.ai_callable()
    async def arrive_meeting(
        self,
        visitor_name: Annotated[str, llm.TypeInfo(description="Name of the visitor.")],
        employee_name: Annotated[str, llm.TypeInfo(description="Name of the employee to meet.")],
        # PIN: Annotated[str, llm.TypeInfo(description="The employee's pin code.")],
    ) -> str:
        """Register a visitor for a meeting."""
        url = f"{API_BASE_URL}/visitors/arrive-meeting"
        payload = {"VisitorName": visitor_name, "MeetingWith": employee_name, "PIN": PIN}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return "The specified employee was not found. Please check the details and try again."   
                else:
                    return f"Failed to register the meeting: {response.status}"

    @llm.ai_callable()
    async def arrive_courier(
        self,
        courier_name: Annotated[str, llm.TypeInfo(description="Name of the courier.")],
    ) -> str:
        """Register a courier arrival."""
        url = f"{API_BASE_URL}/visitors/arrive-courier"
        payload = {"CourierName": courier_name}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return f"Failed to register the courier: {response.status}"

    @llm.ai_callable()
    async def arrive_contractor(
        self,
        contractor_name: Annotated[str, llm.TypeInfo(description="Name of the contractor.")],
        company_name: Annotated[str, llm.TypeInfo(description="Name of the contractor's company.")],
    ) -> str:
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

    @llm.ai_callable()
    async def sign_out(
        self,
        visitor_id: Annotated[int, llm.TypeInfo(description="ID of the visitor to sign out.")],
    ) -> str:
        """Sign out a visitor."""
        url = f"{API_BASE_URL}/visitors/sign-out"
        payload = {"VisitorId": visitor_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return f"Failed to sign out the visitor: {response.status}"

    @llm.ai_callable()
    async def general_enquiry(self) -> str:
        """Handle a general enquiry."""
        logger.info("Reception notified for a general enquiry.")
        return "Reception has been notified. Please wait for assistance."

    @llm.ai_callable()
    async def list_employees(
        self,
        # role: Annotated[int, llm.TypeInfo(description="Admin role ID")],
        pin: Annotated[int, llm.TypeInfo(description="The admin's pin to verify")],
    ) -> str:
        """List employees if the pin is correct."""
        if pin != 123456: 
            return "Invalid PIN. Access denied."
        
        url = f"{API_BASE_URL}/employees"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    employees = await response.json()
                    return f"Employees: {', '.join([emp['name'] for emp in employees])}"
                elif response.status == 403:
                    return "Unauthorized access. Please check your credentials."
                else:
                    return f"Failed to retrieve employees: {response.status}"
                

# Create the FunctionContext
fnc_ctx = VisitorManagementTools()

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
            "You are a voice assistant for visitor management. You can help with tasks such as registering visitors, "
            "couriers, and contractors, signing visitors out, and notifying reception of general enquiries. "
            "If a user requests to view the employee list, ask for the PIN before proceeding."
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


def extract_visitor_name(user_input: str) -> str:
    # Looks for "visitor [name]" or "name is [name]"
    match = re.search(r"(?:visitor\s|name is\s)([a-z\s]+)", user_input, re.IGNORECASE)
    return match.group(1).strip() if match else None

def extract_employee_name(user_input: str) -> str:
    # Looks for "meeting with [name]" or "to meet [name]"
    match = re.search(r"(?:with\s|to meet\s|meeting with\s)([a-z\s]+)", user_input, re.IGNORECASE)
    return match.group(1).strip() if match else None

def extract_id(user_input: str) -> int:
    # Extracts the first number from user input
    match = re.search(r"\d+", user_input)
    return int(match.group(0)) if match else None



if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )