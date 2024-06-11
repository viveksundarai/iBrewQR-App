import streamlit as st
from PIL import Image
import pandas as pd
from pyzbar.pyzbar import decode
import json
import datetime
import os

# Set Streamlit page configuration
st.set_page_config(page_title="PSIPL After Sales Service", page_icon="🔍")

# Function to read QR code
def read_qr_code(image):
    decoded_objects = decode(image)
    if decoded_objects:
        data = decoded_objects[0].data.decode('utf-8')
        return json.loads(data)
    return None

# Function to check warranty status
def check_warranty(data, warranty_df):
    model = data.get("model")
    if not model:
        st.error("Model is missing in the QR code data.")
        return False, False, None, None, None

    warranty_info = warranty_df[warranty_df['Model'] == model]
    if warranty_info.empty:
        st.error("Model number not found in the database.")
        return False, False, None, None, None

    mfg_month = int(warranty_info['Mfg Month'].values[0])
    mfg_year = int(warranty_info['Mfg Year'].values[0])
    warranty_period = int(warranty_info['Warranty (months)'].values[0])
    
    try:
        manufacture_date = datetime.datetime(mfg_year, mfg_month, 1)
    except ValueError:
        st.error("Invalid manufacture date format in warranty data.")
        return False, False, None, None, None

    current_date = datetime.datetime.now()
    warranty_end_date = manufacture_date + datetime.timedelta(days=int(warranty_period) * 30)
    under_warranty = current_date <= warranty_end_date
    
    return True, under_warranty, warranty_info['How to use?'].values[0] if 'How to use?' in warranty_info.columns else None, warranty_info['How to clean?'].values[0] if 'How to clean?' in warranty_info.columns else None, mfg_month, mfg_year

# Function to display registration form
def display_registration_form():
    with st.form("registration_form"):
        name = st.text_input("Name *")
        number = st.text_input("Number *")
        address = st.text_area("Address (optional)")
        company_name = st.text_input("Company Name (optional)")
        gst_number = st.text_input("GST Number (optional)")
        purchased_from = st.text_input("Purchased from (optional)")
        invoice = st.file_uploader("Upload Invoice (optional)", type=['pdf', 'jpg', 'jpeg', 'png'])

        submitted = st.form_submit_button("Register Product")
        if submitted:
            if not name or not number:
                st.error("Name and Number are mandatory fields.")
            else:
                return {
                    "name": name,
                    "number": number,
                    "address": address,
                    "company_name": company_name,
                    "gst_number": gst_number,
                    "purchased_from": purchased_from,
                    "invoice": invoice
                }
    return None

# Function to save customer data
def save_customer_data(data, number):
    df = pd.DataFrame([data])
    file_path = f"C:/01 RVS/01 Personal/04 Learning/08 Streamlit/iBrewQR App/cust-data/{number}.xlsx"
    df.to_excel(file_path, index=False)
    return file_path

# Function to save invoice
def save_invoice(invoice, number):
    if invoice:
        invoice_path = f"C:/01 RVS/01 Personal/04 Learning/08 Streamlit/iBrewQR App/cust-data/{number}_{invoice.name}"
        with open(invoice_path, "wb") as f:
            f.write(invoice.getbuffer())
        return invoice_path
    return None

# Load warranty data
warranty_df = pd.read_excel("C:/01 RVS/01 Personal/04 Learning/08 Streamlit/iBrewQR App/model-warranty.xlsx")

st.image("C:/03 PSIPL/psipl-logo.png", width=150)

# Streamlit app
st.title("After Sale Service")

# QR code upload
st.subheader(":blue[_Please upload QR Code from Gallery or Computer_]", divider='rainbow')
uploaded_file = st.file_uploader("Choose a file", type=['png', 'jpg', 'jpeg'], label_visibility='hidden')

if uploaded_file:
    try:
        image = Image.open(uploaded_file)
        qr_data = read_qr_code(image)

        if qr_data:
            st.subheader(":blue[_Your Warranty Details:_]", divider='rainbow')
            st.write(f"**Model Number:** {qr_data.get('model')}")

            valid, under_warranty, how_to_use_link, how_to_clean_link, mfg_month, mfg_year = check_warranty(qr_data, warranty_df)

            if valid:
                st.write(f"**Month of Manufacture:** {mfg_month}")
                st.write(f"**Year of Manufacture:** {mfg_year}")
                
                if under_warranty:
                    st.success("Product is under warranty.")
                    st.subheader(":blue[_Please register your product to avail warranty services._]", divider='rainbow')
                    registration_data = display_registration_form()
                    if registration_data:
                        save_customer_data(registration_data, registration_data["number"])
                        save_invoice(registration_data["invoice"], registration_data["number"])
                        st.write("Thank you for registering!")
                        
                        # Store registration state in session
                        st.session_state.registered = True
                        st.session_state.choice = None

            if st.session_state.get('registered', False):
                st.subheader(":blue[_What would you like to do next?_]", divider='rainbow')
                choice = st.radio("", ["How to use?", "How to clean?"], key="choice")
                if choice:
                    if choice == "How to use?" and how_to_use_link:
                        st.markdown(how_to_use_link, unsafe_allow_html=True)
                    elif choice == "How to clean?" and how_to_clean_link:
                        st.markdown(how_to_clean_link, unsafe_allow_html=True)
                    else:
                        st.write("No video available for this model.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
