This is the README file.

Set up the environment by filling `.env.local` file by the required values:

- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `OPENAI_API_KEY`

Run the agent with front end </br>

Run the back-end </br>
cd <agent_dir> </br>
python3 -m venv venv </br>
source venv/bin/activate </br>
python3 -m pip install -r requirements.txt </br>
python3 agent.py dev </br>

after that, run the front end </br>
cd <frontend_dir> </br>
pnpm install </br>
pnpm dev </br>

Localhost:
http://localhost:3000
