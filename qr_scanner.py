import streamlit as st
import cv2
from pyzbar.pyzbar import decode
import numpy as np

st.title("QR Code Scanner")

if st.button("Open Camera to Scan QR Code"):
    st.write("Opening camera...")

    # Start capturing video
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            st.write("Failed to grab frame")
            break

        # Decode the QR code
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            # Draw a rectangle around the QR code
            points = obj.polygon
            if len(points) > 4:
                hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                points = hull.reshape((-1, 1, 2))
            points = np.array(points, dtype=np.int32)
            cv2.polylines(frame, [points], True, (0, 255, 0), 2)

            # Display the QR code data
            qr_data = obj.data.decode("utf-8")
            st.write(f"QR Code Data: {qr_data}")

        # Display the video frame with QR code marked
        st.image(frame, channels="BGR")

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
