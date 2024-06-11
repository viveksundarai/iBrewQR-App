import streamlit as st
import qrcode
import json
from PIL import Image
import io

# Function to generate QR code
def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    return img

# Streamlit app
st.title("QR Code Generator")

# Input fields
brand = st.text_input("Brand")
model = st.text_input("Model")
product = st.text_input("Product")
voltage = st.text_input("Voltage")
power = st.text_input("Power")
frequency = st.text_input("Frequency")
capacity = st.text_input("Capacity")
company = st.text_input("Company")
address = st.text_area("Address")
phone = st.text_input("Phone")
compliance = st.text_input("Compliance")
country = st.text_input("Country")

# Combine data into a dictionary
data = {
    "brand": brand,
    "model": model,
    "product": product,
    "voltage": voltage,
    "power": power,
    "frequency": frequency,
    "capacity": capacity,
    "company": company,
    "address": address,
    "phone": phone,
    "compliance": compliance,
    "country": country,
}

# Check if all fields are filled
if all(data.values()):
    # Convert data to JSON string
    data_str = json.dumps(data)

    # Generate QR code
    qr_image = generate_qr_code(data_str)

    # Convert QR code to bytes
    buf = io.BytesIO()
    qr_image.save(buf, format='PNG')
    qr_image_bytes = buf.getvalue()

    # Display QR code
    st.image(qr_image_bytes, caption="Generated QR Code")

    # Download QR code
    buf.seek(0)
    st.download_button(
        label="Download QR Code",
        data=buf,
        file_name="qr_code.png",
        mime="image/png"
    )
else:
    st.write("Please fill in all the fields to generate the QR code.")
