// server.mjs
import express from "express";
import cors from "cors";
import { AccessToken } from "livekit-server-sdk";
import dotenv from "dotenv";

// Load environment variables from .env (optional)
dotenv.config();

const app = express();
app.use(cors());

// Replace these with your actual environment variables or fallback defaults.
const LIVEKIT_URL = process.env.LIVEKIT_URL || "wss://mystreamapp-xg7kywa5.livekit.cloud";
const API_KEY = process.env.LIVEKIT_API_KEY || "YOUR_LIVEKIT_API_KEY";
const API_SECRET = process.env.LIVEKIT_API_SECRET || "YOUR_LIVEKIT_API_SECRET";

// GET /api/connection-details -> Return JSON with serverUrl, roomName, participantName, participantToken
app.get("/api/connection-details", (req, res) => {
  try {
    if (!LIVEKIT_URL || !API_KEY || !API_SECRET) {
      throw new Error("Missing environment variables LIVEKIT_URL, LIVEKIT_API_KEY, or LIVEKIT_API_SECRET");
    }

    // 1) Create random participant & room name
    const participantIdentity = `voice_assistant_user_${Math.floor(Math.random() * 10000)}`;
    const roomName = `voice_assistant_room_${Math.floor(Math.random() * 10000)}`;

    // 2) Create a new AccessToken
    const at = new AccessToken(API_KEY, API_SECRET, {
      identity: participantIdentity,
      ttl: "15m", // token expires after 15 minutes
    });

    // 3) Pass a plain object with the same fields you'd include in a VideoGrant
    at.addGrant({
      room: roomName,
      roomJoin: true,
      canPublish: true,
      canPublishData: true,
      canSubscribe: true,
    });

    // 4) Convert the AccessToken to a signed JWT string
    const participantTokenString = at.toJwt();
    console.log("Generated token:", participantTokenString);

    // 5) Return JSON with the JWT
    const data = {
      serverUrl: LIVEKIT_URL,
      roomName,
      participantName: participantIdentity,
      participantToken: participantTokenString, // The signed JWT string
    };

    res.status(200).json(data);
  } catch (error) {
    console.error("Error generating token:", error);
    res.status(500).json({ error: error.message });
  }
});

// Start the Express server on port 3001 (or your choice)
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
