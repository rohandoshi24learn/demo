const startRecordingButton = document.getElementById("startRecording");
const stopRecordingButton = document.getElementById("stopRecording");
const audioElement = document.getElementById("audioElement");

let audioChunks = [];
let mediaRecorder;
let audioStream;

startRecordingButton.addEventListener("click", async () => {
    audioChunks = [];
    try {
        audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(audioStream);
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };
        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
            audioElement.src = URL.createObjectURL(audioBlob);
            sendAudioToOpenAI(audioBlob);
        };
        mediaRecorder.start();
        startRecordingButton.disabled = true;
        stopRecordingButton.disabled = false;
    } catch (error) {
        console.error("Error accessing audio:", error);
    }
});

stopRecordingButton.addEventListener("click", () => {
    if (mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        startRecordingButton.disabled = false;
        stopRecordingButton.disabled = true;
    }
});

async function sendAudioToOpenAI(audioBlob) {
    // Use your OpenAI API key here
    const apiKey = "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";
    const apiUrl = "https://api.openai.com/v1/audio/transcriptions";

    https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F file="@/path/to/file/audio.mp3" \
  -F model="whisper-1"

    const formData = new FormData();
    formData.append("audio", audioBlob);

    try {
        const response = await fetch(apiUrl, {
            method: "POST",
            body: formData,
            headers: {
                Authorization: `Bearer ${apiKey}`,
            },
        });
        const data = await response.json();
        // console.log("Transcription:", data.choices[0].text);
        console.log("Transcription:", JSON.stringify(data));
    } catch (error) {
        console.error("Error sending audio to OpenAI:", error);
    }
}
