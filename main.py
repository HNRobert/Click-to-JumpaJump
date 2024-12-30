import socket
import cv2
import numpy as np
import struct
import time

# Constants
CHUNK_SIZE = 1024  # Keep consistent with sender's chunk size
PORT = 5000
BUFFER_SIZE = CHUNK_SIZE + 16  # Includes 16 bytes for two 64-bit integers (header information)
RECEIVE_TIMEOUT = 2  # Timeout for waiting for all chunks to arrive (seconds)

# Set up UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', PORT))  # Bind to any IP address, receive data on port 5000
sock.settimeout(RECEIVE_TIMEOUT)  # Set receive timeout

# Socket for sending click coordinates back to server
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('192.168.2.3', 5001)  # Replace with server IP and port for sending coordinates

# Store reassembled image data
image_chunks = {}
clicked_coords = None  # Store mouse click coordinates

# Mouse callback function
def mark_point(event, x, y, flags, param):
    global clicked_coords
    if event == cv2.EVENT_LBUTTONDOWN:
        # Record clicked coordinates
        clicked_coords = (x, y)
        print(f"Mouse clicked at: {clicked_coords}")

        # Pack coordinates into UDP data and send back to server
        data = struct.pack('ii', x, y)  # Pack as two 32-bit integers
        send_sock.sendto(data, server_address)

while True:
    try:
        while True:
            # Receive UDP data
            data, addr = sock.recvfrom(BUFFER_SIZE)

            # Extract header information: chunk index and total number of chunks
            chunk_index = struct.unpack("Q", data[:8])[0]  # First 8 bytes are chunk index
            total_chunks = struct.unpack("Q", data[8:16])[0]  # Next 8 bytes are total number of chunks

            # Extract chunk data
            chunk_data = data[16:]

            # Store chunk data in dictionary with chunk_index as key
            image_chunks[chunk_index] = chunk_data

            # Check if all chunks have been received
            if len(image_chunks) == total_chunks:
                break

    except socket.timeout:
        print("Timeout reached, missing chunks. Skipping this frame.")
        image_chunks.clear()  # Clear data, prepare to receive next frame
        continue

    # Reassemble all chunk data
    try:
        full_image_data = b''.join([image_chunks[i] for i in range(total_chunks)])
    except KeyError as e:
        print(f"Missing chunk: {e}. Skipping this frame.")
        image_chunks.clear()  # Clear data, prepare to receive next frame
        continue

    # Clear dictionary to receive next frame
    image_chunks.clear()

    # Decode JPEG image using OpenCV
    nparr = np.frombuffer(full_image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Display image
    cv2.imshow('Received Image', img)

    # Set mouse click callback
    cv2.setMouseCallback('Received Image', mark_point)

    # Press 'q' key to exit loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Close windows and sockets
cv2.destroyAllWindows()
sock.close()
send_sock.close()
