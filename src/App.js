import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';

const socket = io('http://localhost:8000');

function App() {
  const [stream, setStream] = useState(null);
  const videoRef = useRef();

  useEffect(() => {
    const captureScreen = async () => {
      try {
        const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
        setStream(stream);
        videoRef.current.srcObject = stream;

        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            console.log(event.data)
            socket.emit('screen_data', event.data);
          }
        };
        mediaRecorder.start(100); // Send data every 100ms
      } catch (err) {
        console.error("Error: " + err);
      }
    };

    captureScreen();
  }, []);

  return (
    <div>
      <h1>Screen Capture</h1>
      <video ref={videoRef} autoPlay style={{ width: '100%' }}></video>
    </div>
  );
}

export default App;
