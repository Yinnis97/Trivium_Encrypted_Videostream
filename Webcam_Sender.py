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

def send_webcam_stream():
    """Send webcam frames to Pynq Z2 via TCP"""
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
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
        
        print("Starting to send frames... Press 'q' to quit")
        
        while True:
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame")
                break
            
            # Resize frame to match Pynq expectations
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
            
            # Convert BGR to RGB (OpenCV uses BGR by default)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Flatten frame to 1D array
            frame_data = frame_rgb.tobytes()
            
            # Ensure correct size
            if len(frame_data) != FRAME_SIZE:
                print(f"Warning: Frame size mismatch. Expected {FRAME_SIZE}, got {len(frame_data)}")
                continue
            
            try:
                # Send frame data
                sock.sendall(frame_data)
                frame_count += 1
                
                # Calculate and display FPS every 30 frames
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"Sent {frame_count} frames | FPS: {fps:.2f}")
                
                # Display frame locally (optional)
                cv2.imshow('Sending to Pynq', frame)
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Quit command received")
                    break
                    
            except socket.error as e:
                print(f"Socket error: {e}")
                break
        
    except ConnectionRefusedError:
        print(f"Error: Could not connect to Pynq at {PYNQ_IP}:{PYNQ_PORT}")
        print("Make sure the Pynq is running and the IP address is correct")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        print("\nClosing connection...")
        sock.close()
        cap.release()
        cv2.destroyAllWindows()
        print("Done!")

if __name__ == "__main__":
    send_webcam_stream()