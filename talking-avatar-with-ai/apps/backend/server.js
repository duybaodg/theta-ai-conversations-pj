import cors from "cors";
import dotenv from "dotenv";
import axios from "axios";

import express from "express";
import { openAIChain, parser } from "./modules/openAI.mjs";
import { lipSync } from "./modules/lip-sync.mjs";
import { sendDefaultMessages, defaultResponse } from "./modules/defaultMessages.mjs";
import { convertAudioToText } from "./modules/whisper.mjs";

dotenv.config();

const elevenLabsApiKey = process.env.ELEVEN_LABS_API_KEY;

const app = express();
app.use(express.json());
app.use(cors());
const port = 3000;

const AGENT_API_URL = "http://localhost:8000/generate-response";

app.get("/voices", async (req, res) => {
  res.send(await voice.getVoices(elevenLabsApiKey));
});

app.post("/tts", async (req, res) => {
  const userMessage = await req.body.message;
  const defaultMessages = await sendDefaultMessages({ userMessage });
  if (defaultMessages) {
    res.send({ messages: defaultMessages });
    return;
  }
  let response;
  try {
    const agentResponse = await axios.post(AGENT_API_URL, { question: userMessage });
    console.log(agentResponse.data);

    response = agentResponse.data.messages;
    console.log(response);
  } catch (error) {
    response = defaultResponse;
  }
  response = await lipSync({ messages: response });
  res.send({ messages: response });
});

app.post("/sts", async (req, res) => {
  const base64Audio = req.body.audio;
  const audioData = Buffer.from(base64Audio, "base64");
  const userMessage = await convertAudioToText({ audioData });
  let response;
  try {
    const agentResponse = await axios.post(AGENT_API_URL, { question: userMessage }); 
    response = agentResponse.data.messages;
  } catch (error) {
    response = defaultResponse;
  }
  response = await lipSync({ messages: response });
  res.send({ messages: response });
});

app.listen(port, () => {
  console.log(`Aria are listening on port ${port}`);
});
