import websocket
import json
import pyaudio
import wave
import base64
import threading

# Server configuration
SERVER_URL = "ws://127.0.0.1:8090/paddlespeech/asr/streaming"

# Audio configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

class ASRClient:
    def __init__(self):
        self.ws = None
        self.is_running = False

    def on_message(self, ws, message):
        data = json.loads(message)
        #print(data)
        if 'result' in data:
            #print(f"ASR Result: {data['result']}")
            print(f"ASR Result: {data}")

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")

    def on_open(self, ws):
        print("WebSocket connection opened")
        self.send_start_signal()

    def send_start_signal(self):
        start_signal = json.dumps({
            "name": "test.wav",
            "signal": "start",
            "nbest": 1
        })
        self.ws.send(start_signal)

    def send_audio_data(self, audio_data):
        self.ws.send(audio_data, websocket.ABNF.OPCODE_BINARY)

    def send_end_signal(self):
        end_signal = json.dumps({
            "name": "test.wav",
            "signal": "end",
            "nbest": 1
        })
        self.ws.send(end_signal)

    def start_recognition(self):
        self.is_running = True
        #websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(SERVER_URL,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)

        wst = threading.Thread(target=self.ws.run_forever)
        wst.start()

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("* Recording")

        try:
            while self.is_running:
                data = stream.read(CHUNK)
                self.send_audio_data(data)
        except KeyboardInterrupt:
            print("* Stopped recording")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            self.send_end_signal()
            self.is_running = False
            self.ws.close()

if __name__ == "__main__":
    client = ASRClient()
    client.start_recognition()
