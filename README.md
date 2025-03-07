# Visitor Management and Sales Agency AI Assistant

Welcome to the our project! This innovative application leverages the power of AI to provide instant receptionist and sales assistant to users.

## Overview

This project demonstrates the integration of LiveKit for real-time communication, OpenAI for natural language processing, and a modern React/Next.js frontend to create an engaging AI-powered sales assistant.

## Features

- Real-time video and audio communication
- AI-powered chat assistance for sales queries
- Modern, responsive user interface
- Dynamic background animations
- Seamless integration with LiveKit and OpenAI APIs

## License

This project is licensed under the Apache-2.0 license - see the [LICENSE](LICENSE) file for details.

# Backend Voice Agent - Powered by LiveKIT

## Dev Setup

1. Clone the repository and install dependencies to a virtual environment:

```console
cd theta-ai-conversations-pj
cd <agent_dir>
python3 -m venv venv
source venv/bin/activate (for Mac)
.\venv\Scripts\activate (for Windows)
pip install -r requirements.txt
```

2. Set up the environment in `.env.local` and filling in the required values:

- LIVEKIT_API_KEY=<your API KEY>
- LIVEKIT_API_SECRET=<Your API Secret>
- NEXT_PUBLIC_LIVEKIT_URL=wss://<Your Cloud URL>
- OPENAI_API_KEY=<your OpenAPI Key>

3. Run the agent:

```console

python3 agentNew.py start
```

## Getting Started Frontend

1. Clone the repository
2. Install dependencies

```console
cd <Agent-UI>
npm install
```

3. Set up the Environment for Livekit Rom by update .evn.local file:
   LIVEKIT_API_KEY=<your API KEY>
   LIVEKIT_API_SECRET=<Your API Secret>
   NEXT_PUBLIC_LIVEKIT_URL=wss://<Your Cloud URL>
4. Run the development server with

```console

npm run dev`
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser
