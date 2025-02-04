from __future__ import annotations
import logging
import re
import requests
from dotenv import load_dotenv
import os
from livekit import rtc
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai
import aiohttp
from typing import Annotated

# Load environment variables
load_dotenv(dotenv_path=".env.local")

# API Base URL
API_BASE_URL = os.getenv("API_BASE_URL")
print(f"Loaded url: {API_BASE_URL}") 

# API Base URL
ADMIN_PIN = os.getenv("ADMIN_PIN")
print(f"Loaded url: {ADMIN_PIN}") 

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")
print(f"Using Teams Webhook URL: {TEAMS_WEBHOOK_URL}")

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
    ) -> str:
        """Register a visitor for a meeting."""
        url = f"{API_BASE_URL}/visitors/arrive-meeting"
        payload = {"visitorName": visitor_name, "meetingWith": employee_name}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                return await response.json()

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
                return await response.json()
                # if response.status == 200:
                #     return await response.json()
                # else:
                #     return f"Failed to register the courier: {response.status}"

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
                return await response.json()

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
                return await response.json()

    @llm.ai_callable()
    async def general_enquiry(self) -> str:
        """Notify reception when a visitor makes a general enquiry."""
        
        message = "A visitor has a general enquiry. Please assist at the front desk."
        return notify_reception(message)

    @llm.ai_callable()
    async def list_employees(
        self,
        include_email: Annotated[bool, llm.TypeInfo(description="Include email addresses if True.")]
    ) -> str:
        """List employees if the pin is correct. Optionally include email addresses and IDs if requested. """
    
        logger.debug("Admin PIN verified. Fetching employee list...")

        url = f"{API_BASE_URL}/employees"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                # return await response.json()
                if response.status == 200:
                    employees = await response.json()
                    logger.debug(f"Employee Data: {employees}")
        
                    if include_email:
                        # Include both name and email
                        employee_details = ', '.join([f"{emp['name']} ({emp['email']})" for emp in employees])
                    else:
                        # Only include names
                        employee_details = ', '.join([emp['name'] for emp in employees])

                    return f"Employees: {employee_details}"
                # elif response.status == 403:
                #     return "Unauthorized access. Please check your credentials."
                # else:
                #     return f"Failed to retrieve employees: {response.status}"
                

    @llm.ai_callable()
    async def list_onsite(
        self
    ) -> str:
        """List people onsite if the pin is correct."""

        logger.debug("Admin PIN verified. Fetching onsite list...")

        url = f"{API_BASE_URL}/on_site"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                # return await response.json()
                if response.status == 200:
                    on_site = await response.json()
                    logger.debug(f"Onsite Data: {on_site}")
        
                    onsite_details = ', '.join([f"{person['name']} ({person['type']})" for person in on_site])

                    return f"Onsite: {onsite_details}"
                # elif response.status == 403:
                #     return "Unauthorized access. Please check your credentials."
                # else:
                #     return f"Failed to retrieve employees: {response.status}"


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
    logger.debug(f"ADMIN PIN: {ADMIN_PIN}")
    model = openai.realtime.RealtimeModel(
        instructions=(
            # "You are a voice assistant for visitor management. Your first action should always be to greet the users. "
            # "You can help with tasks such as registering visitors, "
            # "couriers, and contractors, signing visitors out, and notifying reception of general enquiries. "
            # "If a user requests to view the employee list or people onsite, ask for the PIN before proceeding. "
            # "Repeat the PIN that the user has provided, "
            # "the PIN should be an exact match of the four digits. If the PIN is incorrect, do not give the employee list or the people onsite list. "     
            "You are a voice assistant for visitor management. Your first action should always be to greet the users. "
            "You can help with tasks such as registering visitors, couriers, and contractors, signing visitors out, and notifying reception of general enquiries. "
            "If a user requests to view the employee list or people onsite, ask for the four-digit PIN before proceeding. "
            "Once the user provides a PIN, repeat it back, wait for the user confirmation, then verify if the PIN matches the correct one. "
            "If the PIN is correct, provide the requested information. If the PIN is incorrect, do not give the information and inform the user that the PIN is invalid. "
            "If the user does not confirm the PIN, ask them to provide it again. "
            "If you encounter an issue or a problem with their request, ask if they would like to see the receptionist. "
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


def notify_reception(message: str) -> str:
    """Send a notification to both Microsoft Teams and Slack."""
    
    logger.info("Notifying reception via Microsoft Teams and Slack.")

    headers = {"Content-Type": "application/json"}

    # Microsoft Teams
    teams_message = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "size": "Large",
                            "weight": "Bolder",
                            "text": "VISITOR ASSISTANCE NEEDED"
                        },
                        {
                            "type": "TextBlock",
                            "text": message,
                            "wrap": True
                        },
                        {
                            "type": "TextBlock",
                            "text": "Request acknowledged by Reception",
                            "wrap": True,
                            "id": "acknowledgedText",
                            "isVisible": False
                        }
                    ],
                    # "actions": [
                    #     {
                    #         "type": "Action.Submit",
                    #         "title": "Acknowledge",
                    #         "data": {
                    #             "action": "acknowledge_request",
                    #             "message": message
                    #         }
                    #     }
                    # ],
                    # "refresh": {
                    #     "action": {
                    #         "type": "Action.Execute",
                    #         "verb": "refresh_acknowledgment",
                    #         "data": {
                    #             "message": message
                    #         }
                    #     }
                    "actions": [
                        {
                            "type": "Action.ToggleVisibility",
                            "title": "Acknowledge",
                            "targetElements": ["acknowledgedText"]
                        }
                    ]
                }
            }
        ]
    }

    # Slack Message
    slack_message = {
        "text": f"*Visitor Assistance Needed* \n{message}"
    }

    # Send to Microsoft Teams
    teams_response = requests.post(TEAMS_WEBHOOK_URL, json=teams_message, headers=headers)

    # Send to Slack
    slack_response = requests.post(SLACK_WEBHOOK_URL, json=slack_message, headers=headers)

    # Check Responses
    if teams_response.status_code == 200 and slack_response.status_code == 200:
        return "Reception has been notified via Microsoft Teams and Slack."
    elif teams_response.status_code != 200:
        logger.error(f"Failed to notify Teams: {teams_response.status_code} - {teams_response.text}")
        return f"Failed to notify Teams: {teams_response.status_code}"
    elif slack_response.status_code != 200:
        logger.error(f"Failed to notify Slack: {slack_response.status_code} - {slack_response.text}")
        return f"Failed to notify Slack: {slack_response.status_code}"


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )