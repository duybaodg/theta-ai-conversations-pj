import { OpenAIWhisperAudio } from "langchain/document_loaders/fs/openai_whisper_audio";
import { convertAudioToMp3 } from "../utils/audios.mjs";
import fs from "fs";
import dotenv from "dotenv";
dotenv.config();

const openAIApiKey = process.env.OPENAI_API_KEY;

async function convertAudioToText({ audioData }) {
  // Convert the audio data to MP3
  const mp3AudioData = await convertAudioToMp3({ audioData });
  const outputPath = "/tmp/output.mp3";
  
  // Write the converted audio data to a temporary file
  fs.writeFileSync(outputPath, mp3AudioData);
  
  // Create a new loader instance using the public API
  const loader = new OpenAIWhisperAudio(outputPath, { clientOptions: { apiKey: openAIApiKey } });
  
  // Load and process the transcription document
  const doc = (await loader.load()).shift();
  const transcribedText = doc.pageContent;
  
  // Clean up the temporary file
  fs.unlinkSync(outputPath);
  
  return transcribedText;
}

export { convertAudioToText };
