"""
tcp_video_client.py
Stream 24-bit RGB video over TCP to a server.
"""

import argparse
import socket
import struct
import time
import cv2

HEADER_FMT = "!IHH"   # frame_size(uint32), width(uint16), height(uint16)
HEADER_SIZE = struct.calcsize(HEADER_FMT)

def main():
    parser = argparse.ArgumentParser(description="TCP RGB video client streamer")
    parser.add_argument("--host", required=True, help="Server address")
    parser.add_argument("--port", type=int, required=True, help="TCP port")
    parser.add_argument("--file", help="Optional video file, otherwise webcam is used")
    parser.add_argument("--width", type=int, default=320)
    parser.add_argument("--height", type=int, default=240)
    parser.add_argument("--fps", type=float, default=0.5)
    parser.add_argument("--src-index", type=int, default=0)
    args = parser.parse_args()

    # Open video source
    if args.file:
        cap = cv2.VideoCapture(args.file)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open file: {args.file}")
    else:
        cap = cv2.VideoCapture(args.src_index)

    # Connect to server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connecting to {args.host}:{args.port}...")
    client.connect((args.host, args.port))
    print(f"Connected to server!")

    frame_interval = 1.0 / args.fps

    try:
        while True:
            start = time.time()

            ret, frame = cap.read()
            if not ret:
                if args.file:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    time.sleep(0.05)
                    continue

            # Prepare RGB frame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (args.width, args.height))
            raw = frame.tobytes()

            # Build header
            header = struct.pack(
                HEADER_FMT,
                len(raw),
                args.width,
                args.height
            )

            # Send header + frame
            client.sendall(header + raw)

            # FPS pacing
            elapsed = time.time() - start
            if elapsed < frame_interval:
                time.sleep(frame_interval - elapsed)

    except (BrokenPipeError, ConnectionResetError):
        print("Server disconnected.")
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        client.close()
        cap.release()

if __name__ == "__main__":
    main()