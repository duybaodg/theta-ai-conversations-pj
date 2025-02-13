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
        url_post = f"{API_BASE_URL}/visitors/arrive-meeting"
        url_get = f"{API_BASE_URL}/visitors"

        payload = {"visitorName": visitor_name, "meetingWith": employee_name}
        async with aiohttp.ClientSession() as session:
            async with session.post(url_post, json=payload) as response:
                if response.status != 200:
                    return f"Failed to register visitor: {await response.text()}"

            async with session.get(url_get) as response:
                # return await response.json()

                visitors = await response.json()

            for visitor in sorted(visitors, key=lambda v: v.get("arrivalTime", ""), reverse=True):
                if visitor.get("name") == visitor_name and visitor.get("meetingWith") == employee_name:
                    visitor_id = visitor.get("id")
                    return f"Visitor {visitor_name} has been registered successfully. Your visitor ID is {visitor_id}. Please keep this ID for sign-out."



    @llm.ai_callable()
    async def arrive_courier(
        self,
        courier_name: Annotated[str, llm.TypeInfo(description="Name of the courier.")],
    ) -> str:
        """Register a courier arrival."""
        url_post = f"{API_BASE_URL}/visitors/arrive-courier"
        url_get = f"{API_BASE_URL}/visitors"
        payload = {"CourierName": courier_name}
  
        async with aiohttp.ClientSession() as session:
            async with session.post(url_post, json=payload) as response:
                if response.status != 200:
                    return f"Failed to register visitor: {await response.text()}"

            async with session.get(url_get) as response:
                # return await response.json()

                visitors = await response.json()

            for visitor in sorted(visitors, key=lambda v: v.get("arrivalTime", ""), reverse=True):
                if visitor.get("name") == courier_name and visitor.get("reason") == 'Courier':
                    visitor_id = visitor.get("id")
                    return f"Courier {courier_name} has been registered successfully. Your visitor ID is {visitor_id}. Please keep this ID for sign-out."


    @llm.ai_callable()
    async def arrive_contractor(
        self,
        contractor_name: Annotated[str, llm.TypeInfo(description="Name of the contractor.")],
        company_name: Annotated[str, llm.TypeInfo(description="Name of the contractor's company.")],
    ) -> str:
        """Register a contractor arrival."""
        url_post = f"{API_BASE_URL}/visitors/arrive-contractor"
        url_get = f"{API_BASE_URL}/visitors"
        payload = {"VisitorName": contractor_name, "Company": company_name}
        async with aiohttp.ClientSession() as session:
            async with session.post(url_post, json=payload) as response:
                if response.status != 200:
                    return f"Failed to register visitor: {await response.text()}"

            async with session.get(url_get) as response:
                # return await response.json()

                visitors = await response.json()

            for visitor in sorted(visitors, key=lambda v: v.get("arrivalTime", ""), reverse=True):
                if visitor.get("name") == contractor_name and visitor.get("contractorCompany") == company_name:
                    visitor_id = visitor.get("id")
                    return f"Contractor {contractor_name} has been registered successfully. Your visitor ID is {visitor_id}. Please keep this ID for sign-out."


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
        
        notification = "GENERAL ENQUIRY"
        message = "A visitor has a general enquiry. Please assist at the front desk."
        return notify_reception(notification,message)
    
    @llm.ai_callable()
    async def call_reception(self) -> str:
        """Notify reception for assistance."""
        
        notification = "VISITOR ASSISTANCE NEEDED"
        message = "A visitor has a needs assistance with their request. Please assist at the front desk."
        return notify_reception(notification, message)


    @llm.ai_callable()
    async def list_employees(
        self,
        pin: Annotated[str, llm.TypeInfo(description="Four-digit PIN for access verification.")],
        include_email: Annotated[bool, llm.TypeInfo(description="Include email addresses if True.")]
    ) -> str:
        """List employees if the pin is correct. Optionally include email addresses and IDs if requested. """
    
        if pin != ADMIN_PIN:
            logger.warning(f"Incorrect PIN entered: {pin}")
            return "Invalid PIN. Access denied."

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

    @llm.ai_callable()
    async def list_onsite(
        self,
        pin: Annotated[str, llm.TypeInfo(description="Four-digit PIN for access verification.")],
    ) -> str:
        """List people onsite if the pin is correct."""

        if pin != ADMIN_PIN:
            logger.warning(f"Incorrect PIN entered: {pin}")
            return "Invalid PIN. Access denied."

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

    @llm.ai_callable()
    async def visitors_onsite(
        self,
        pin: Annotated[str, llm.TypeInfo(description="Four-digit PIN for access verification.")],
    ) -> str:
        """List visitors onsite if the pin is correct."""

        if pin != ADMIN_PIN:
            logger.warning(f"Incorrect PIN entered: {pin}")
            return "Invalid PIN. Access denied."

        logger.debug("Admin PIN verified. Fetching visitors onsite list...")

        url = f"{API_BASE_URL}/visitors/on-site"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                # return await response.json()
                if response.status == 200:
                    visitor_onsite = await response.json()
                    logger.debug(f"Visitors onsite Data: {visitor_onsite}")
        
                    visitor_onsite = ', '.join([f"{person['name']} ({person['reason']})" for person in visitor_onsite])

                    return f"Onsite: {visitor_onsite}"


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
            "You are a voice assistant for visitor management. Your first action should always be to greet the users. "
            "You can help with tasks such as registering visitors, couriers, and contractors, "
            "signing visitors out, and notifying reception of general enquiries. "
            "For security-sensitive requests, such as viewing the employee list, people onsite, or visitors onsite "
            "you must follow these steps: "
            "1. **Request a four-digit PIN from the user.** "
            "2. **Repeat the PIN back to the user for confirmation.** "
            "3. **Verify the PIN against the correct stored PIN.** " 
            "4. **Only proceed if the PIN matches exactly.** "
            "- If the PIN is correct, retrieve the requested information. "
            "- If the PIN is incorrect, deny access and inform the user that they need the correct PIN. "
            "5. **If the user does not provide a PIN or refuses to confirm it, do not proceed with the request.** "
            "6. **If there are multiple incorrect attempts, suggest contacting the receptionist for assistance.** "
        ),
        modalities=["audio", "text"],
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


def notify_reception(notification: str, message: str) -> str:
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
                            "text": notification,
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