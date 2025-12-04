import socket
import cv2
import numpy as np
import time

# Configuration
PYNQ_IP = "192.168.2.81"  # Change to your Pynq Z2 IP address
PYNQ_PORT = 7
FRAME_WIDTH = 320
FRAME_HEIGHT = 240
FRAME_SIZE = FRAME_WIDTH * FRAME_HEIGHT * 3  # RGB

def receive_frame_data(sock, size):
    """Receive exactly 'size' bytes from socket"""
    data = b''
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            return None
        data += packet
    return data

def receive_pynq_stream():
    """Receive and display frames from Pynq Z2 via TCP"""
    
    try:
        # Connect to Pynq
        print(f"Connecting to Pynq at {PYNQ_IP}:{PYNQ_PORT}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((PYNQ_IP, PYNQ_PORT))
        print("Connected successfully!")
        
        # Receive welcome message
        welcome = sock.recv(1024).decode('utf-8')
        print(f"Server says: {welcome}")
        
        # === HANDSHAKE: Wait for user to send start message ===
        print("\n" + "="*50)
        print("Connection established. Ready to stream.")
        print("="*50)
        start_msg = input("Enter a message to start streaming (e.g., 'START'): ").strip()
        
        if not start_msg:
            start_msg = "START"  # Default message
        
        # Send the handshake message with newline delimiter
        handshake = (start_msg + "\0").encode('utf-8')
        sock.sendall(handshake)
        print(f"Sent handshake: '{start_msg}'")
        
        frame_count = 0
        start_time = time.time()
        
        print("Waiting for frames from Pynq... Press 'q' to quit")
        
        while True:
            # Receive frame data
            frame_data = receive_frame_data(sock, FRAME_SIZE)
            
            if frame_data is None:
                print("Connection closed by Pynq")
                break
            
            if len(frame_data) != FRAME_SIZE:
                print(f"Warning: Incomplete frame received. Expected {FRAME_SIZE}, got {len(frame_data)}")
                continue
            
            # Convert bytes to numpy array
            frame_array = np.frombuffer(frame_data, dtype=np.uint8)
            
            # Reshape to image dimensions (RGB)
            frame_rgb = frame_array.reshape((FRAME_HEIGHT, FRAME_WIDTH, 3))
            
            # Convert RGB to BGR for OpenCV display
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            
            frame_count += 1
            
            # Calculate and display FPS every 30 frames
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                print(f"Received {frame_count} frames | FPS: {fps:.2f}")
            
            # Display frame
            cv2.imshow('Received from Pynq', frame_bgr)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Quit command received")
                break
        
    except ConnectionRefusedError:
        print(f"Error: Could not connect to Pynq at {PYNQ_IP}:{PYNQ_PORT}")
        print("Make sure the Pynq is running and the IP address is correct")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print("\nClosing connection...")
        sock.close()
        cv2.destroyAllWindows()
        print("Done!")

if __name__ == "__main__":
    receive_pynq_stream()