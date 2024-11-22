# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from websocket import create_connection, WebSocketException
import json
import base64
import hashlib
import threading
import time

app = Flask(__name__)
# APP Config
APP_PORT = "5987"

# Config OBS WebSocket
OBS_WEBSOCKET_URL = "ws://127.0.0.1:4455"
OBS_PASSWORD = "obswebsocketpassword"

# Nom des scènes
BRB_SCENE = "BRB"
MAIN_SCENE = "MAIN"
CAMERA_SOURCE_NAME = "Flux"

# Bitrate threshold in kb/s to determine if the stream is correct
BITRATE_THRESHOLD = 1000  # Ajust for your needs

# Last state position to know if the stream is freezed
last_cursor_position = None
last_frame_timecode = None




/////////////////// DONT MODIFY IF YOU DONT KNOW WHAT YOU DO /////////////////// 


def calculate_auth_hash(password, challenge, salt):
    """Calculate the authentication hash for OBS WebSocket."""
    try:
        secret = base64.b64encode(
            hashlib.sha256((password + salt).encode("utf-8")).digest()
        ).decode("utf-8")
        auth_response = base64.b64encode(
            hashlib.sha256((secret + challenge).encode("utf-8")).digest()
        ).decode("utf-8")
        return auth_response
    except Exception as e:
        print(f"Error calculating authentication hash: {e}")
        return None


def send_obs_request(request_type, request_data=None):
    """Send a request to OBS WebSocket."""
    try:
        ws = create_connection(OBS_WEBSOCKET_URL, timeout=5)
        hello_message = json.loads(ws.recv())
        rpc_version = hello_message["d"]["rpcVersion"]
        if "authentication" in hello_message["d"]:
            challenge = hello_message["d"]["authentication"]["challenge"]
            salt = hello_message["d"]["authentication"]["salt"]
            auth_hash = calculate_auth_hash(OBS_PASSWORD, challenge, salt)
        else:
            auth_hash = None

        identify_payload = {"op": 1, "d": {"rpcVersion": rpc_version}}
        if auth_hash:
            identify_payload["d"]["authentication"] = auth_hash

        ws.send(json.dumps(identify_payload))
        identified_message = json.loads(ws.recv())
        if identified_message["op"] != 2:
            ws.close()
            print("Failed to identify with OBS WebSocket.")
            return {"error": "Failed to identify with OBS WebSocket"}

        payload = {
            "op": 6,
            "d": {
                "requestType": request_type,
                "requestId": "1",
                "requestData": request_data if request_data else {},
            },
        }
        ws.send(json.dumps(payload))
        response = json.loads(ws.recv())
        ws.close()
        return response
    except WebSocketException as e:
        print(f"WebSocket error: {e}")
        return {"error": "WebSocket error"}
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}


def get_media_cursor(source_name):
    """Get the current media cursor position for a source."""
    response = send_obs_request("GetMediaInputStatus", {"inputName": source_name})
    if "error" not in response:
        return response["d"]["responseData"].get("mediaCursor")
    return None


def is_source_frozen(source_name):
    """Check if the source is frozen by comparing mediaCursor."""
    global last_cursor_position
    current_cursor_position = get_media_cursor(source_name)

    if current_cursor_position is None:
        print(f"Could not retrieve cursor for source '{source_name}'. Assuming frozen.")
        return True

    if current_cursor_position == last_cursor_position:
        print(f"Source '{source_name}' is frozen (cursor not moving).")
        return True

    print(f"Source '{source_name}' is not frozen (cursor is moving).")
    last_cursor_position = current_cursor_position
    return False


def change_scene(new_scene):
    """Change the OBS scene."""
    print(f"Attempting to change scene to: {new_scene}")
    response = send_obs_request("SetCurrentProgramScene", {"sceneName": new_scene})
    if response.get("error"):
        print(f"Failed to change scene to {new_scene}: {response['error']}")
        return False
    return True


def get_current_scene():
    """Get the current OBS scene."""
    response = send_obs_request("GetCurrentProgramScene")
    if "error" in response:
        print(f"Error getting current scene: {response['error']}")
        return None
    return response["d"]["responseData"]["currentProgramSceneName"]


def monitor_bitrate_and_freeze():
    """Monitor the RTMP/SRT stream and OBS source freeze, change OBS scene if needed."""
    current_scene = get_current_scene() or MAIN_SCENE

    while True:
        try:
            print("----- Monitoring loop start -----")

            # Vérification si la source est gelée
            if is_source_frozen(CAMERA_SOURCE_NAME):
                if current_scene != BRB_SCENE:
                    print("Source is frozen. Switching to BRB scene.")
                    if change_scene(BRB_SCENE):
                        current_scene = BRB_SCENE
                else:
                    print("Already on BRB scene (source frozen).")
            else:
                # Vérification de la scène actuelle
                current_scene_from_obs = get_current_scene()
                if current_scene_from_obs != current_scene:
                    print(
                        f"Scene mismatch detected. Updating current_scene to {current_scene_from_obs}."
                    )
                    current_scene = current_scene_from_obs

                # Retour à la scène principale si tout est normal
                if current_scene != MAIN_SCENE:
                    print("Source is active. Switching back to Main scene.")
                    if change_scene(MAIN_SCENE):
                        current_scene = MAIN_SCENE

            print("----- Monitoring loop end -----\n")
            time.sleep(5)
        except Exception as e:
            print(f"Exception in monitoring loop: {e}")
            time.sleep(5)


@app.route("/start", methods=["GET"])
def start_stream():
    """Start OBS stream."""
    result = send_obs_request("StartStream")
    return jsonify(result)


@app.route("/stop", methods=["GET"])
def stop_stream():
    """Stop OBS stream."""
    result = send_obs_request("StopStream")
    return jsonify(result)


if __name__ == "__main__":
    # Start the monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_bitrate_and_freeze)
    monitor_thread.daemon = True
    monitor_thread.start()

    # Start the Flask app
    app.run(host="0.0.0.0", port=APP_PORT)
