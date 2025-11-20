import argparse
import socket
import cv2
import numpy as np

FRAME_WIDTH = 320
FRAME_HEIGHT = 240
FRAME_SIZE = FRAME_WIDTH * FRAME_HEIGHT * 3  # RGB


def recv_exact(sock, num_bytes):
    """Receive exactly num_bytes from socket."""
    data = b''
    while len(data) < num_bytes:
        chunk = sock.recv(num_bytes - len(data))
        if not chunk:
            raise ConnectionError("Connection closed")
        data += chunk
    return data


def main():
    parser = argparse.ArgumentParser(description="Live RGB frame viewer")
    parser.add_argument("--host", required=True, help="PYNQ server IP")
    parser.add_argument("--port", type=int, required=True, help="TCP port")
    args = parser.parse_args()

    # Connect to server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connecting to {args.host}:{args.port}...")
    client.connect((args.host, args.port))
    print("Connected!")

    # Handshake
    client.sendall(b"READY\0")

    try:
        while True:
            # --- Receive one frame ---
            data = recv_exact(client, FRAME_SIZE)

            # Convert to numpy image
            frame = np.frombuffer(data, dtype=np.uint8).reshape(
                (FRAME_HEIGHT, FRAME_WIDTH, 3)
            )

            # Convert RGB → BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Display frame
            cv2.imshow("Live Stream", frame_bgr)

            # Press ESC to quit
            if cv2.waitKey(1) == 27:
                break

    except ConnectionError:
        print("Connection closed by device.")
    finally:
        client.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
