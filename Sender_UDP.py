import cv2
import socket
import struct

# -------- CONFIG --------
TARGET_IP = "192.168.1.10" #"127.0.0.1" 
TARGET_PORT = 5005
# ------------------------

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Could not open webcam")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Encode frame as JPEG
    _, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
    data = encoded.tobytes()

    # Split data into chunks
    max_size = 65000
    total = len(data)
    num_chunks = (total // max_size) + 1

    for i in range(num_chunks):
        chunk = data[i*max_size:(i+1)*max_size]
        # header: chunk index + total chunks
        header = struct.pack("HH", i, num_chunks)
        sock.sendto(header + chunk, (TARGET_IP, TARGET_PORT))

cap.release()
sock.close()
