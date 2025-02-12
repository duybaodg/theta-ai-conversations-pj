"use client";

import React, { useCallback, useEffect, useState } from "react";

// --- Three.js and Chat Interface Imports ---
import { Loader } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { Leva } from "leva";
import { Scenario } from "./components/Scenario";
import { ChatInterface } from "./components/ChatInterface";

// --- LiveKit and Related Imports ---
import { AnimatePresence, motion } from "framer-motion";
import {
  LiveKitRoom,
  useVoiceAssistant,
  BarVisualizer,
  RoomAudioRenderer,
  VoiceAssistantControlBar,
  DisconnectButton,
} from "@livekit/components-react";
import { NoAgentNotification } from "./components/NoAgentNotification";
import { CloseIcon } from "./components/CloseIcon";

/**
 * Optionally define this outside the component
 */
async function fetchConnectionDetails() {
  try {
    const response = await fetch("http://localhost:3000/api/connection-details");
    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }
    const data = await response.json();
    console.log("Received connection details:", data);
    return data;
  } catch (err) {
    console.error("Error fetching connection details:", err);
    throw err;
  }
}

function App() {
  const [connectionDetails, updateConnectionDetails] = useState(null);
  const [agentState, setAgentState] = useState("disconnected");

  /**
   * Use the fetchConnectionDetails function inside onConnectButtonClicked
   */
  const onConnectButtonClicked = useCallback(async () => {
    try {
      const data = await fetchConnectionDetails();
      updateConnectionDetails(data);
    } catch (err) {
      console.error("Failed to fetch details:", err);
    }
  }, []);

  return (
    <div className="relative w-full h-screen">
      {/* --- Three.js and Chat UI --- */}
      <Loader />
      <Leva collapsed hidden />
      <Canvas shadows camera={{ position: [0, 0, 0], fov: 10 }}>
        <Scenario />
      </Canvas>

      {/* --- Conversation UI Overlay --- */}
      <div className="absolute top-0 left-0 w-full h-full z-50 pointer-events-none">
        <main
          data-lk-theme="default"
          className="h-full grid content-center bg-[var(--lk-bg)] pointer-events-auto"
        >
          <LiveKitRoom
            token={connectionDetails?.participantToken}
            serverUrl={connectionDetails?.serverUrl}
            connect={connectionDetails !== null}
            audio={true}
            video={false}
            onMediaDeviceFailure={onDeviceFailure}
            onDisconnected={() => {
              updateConnectionDetails(null);
            }}
            className="grid grid-rows-[2fr_1fr] items-center"
          >
            <SimpleVoiceAssistant onStateChange={setAgentState} />
            <ControlBar
              onConnectButtonClicked={onConnectButtonClicked}
              agentState={agentState}
            />
            <RoomAudioRenderer />
            <NoAgentNotification state={agentState} />
          </LiveKitRoom>
        </main>
      </div>
    </div>
  );
}

function SimpleVoiceAssistant({ onStateChange }) {
  const { state, audioTrack } = useVoiceAssistant();

  useEffect(() => {
    onStateChange(state);
  }, [onStateChange, state]);

  return (
    <div className="h-[300px] max-w-[90vw] mx-auto">
      <BarVisualizer
        state={state}
        barCount={5}
        trackRef={audioTrack}
        className="agent-visualizer"
        options={{ minHeight: 24 }}
      />
    </div>
  );
}

function ControlBar({ onConnectButtonClicked, agentState }) {
  return (
    <div className="relative h-[600px]">
      <AnimatePresence>
        {agentState === "disconnected" && (
          <motion.button
            initial={{ opacity: 0, top: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, top: "-10px" }}
            transition={{ duration: 1, ease: [0.09, 1.04, 0.245, 1.055] }}
            className="uppercase absolute left-1/2 px-2 py-2 bg-white text-black rounded-md"
            onClick={onConnectButtonClicked}
          >
            Start a conversation
          </motion.button>
        )}
      </AnimatePresence>
      <AnimatePresence>
        {agentState !== "disconnected" && agentState !== "connecting" && (
          <motion.div
            initial={{ opacity: 0, top: "10px" }}
            animate={{ opacity: 1, top: 0 }}
            exit={{ opacity: 0, top: "-10px" }}
            transition={{ duration: 0.4, ease: [0.09, 1.04, 0.245, 1.055] }}
            className="flex h-8 absolute left-1/2 -translate-x-1/2 justify-center"
          >
            <VoiceAssistantControlBar controls={{ leave: false }} />
            <DisconnectButton>
              <CloseIcon />
            </DisconnectButton>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function onDeviceFailure(error) {
  console.error(error);
  alert(
    "Error acquiring camera or microphone permissions. Please ensure you grant the necessary permissions in your browser and reload the tab."
  );
}

export default App;
