import { Loader } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { Leva } from "leva";
import { Scenario } from "./components/Scenario";
import { ChatInterface } from "./components/ChatInterface";
import { useState } from "react";

function App() {
  const [isConnected, setIsConnected] = useState(false);

  const handleConnect = () => {
    // Add your connect logic here
    setIsConnected(true);
    console.log("Connected");
  };

  return (
    <>
      <Loader />
      <Leva collapsed hidden/>
      <ChatInterface />
      {!isConnected && (
        <button onClick={handleConnect} className="connect-button">
          Connect
        </button>
      )}
      <Canvas shadows camera={{ position: [0, 0, 0], fov: 10 }}>  
      <Scenario />
      </Canvas>
    </>
  );
}

export default App;
