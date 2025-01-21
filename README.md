This is the README file.

Set up the environment by filling `.env.local` file by the required values:

- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `OPENAI_API_KEY`

Run the agent with front end

Run the back-end
cd <agent_dir>
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 agent.py dev

after that, run the front end
cd <frontend_dir>
pnpm install
pnpm dev

Localhost:
http://localhost:3000
