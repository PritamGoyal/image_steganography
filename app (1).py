import streamlit as st
from PIL import Image
import tempfile
import base64
from stegano import encrypt, decrypt, encodeImage, decodeImage, convertToRGB, headerText

st.set_page_config(page_title="🔐 Image Steganography", layout="centered")
st.title("🔐 Image Steganography with AES Encryption")

mode = st.radio("Choose Mode:", ["Encode", "Decode"])

if mode == "Encode":
    uploaded_image = st.file_uploader("Upload Cover Image", type=["png", "jpg", "jpeg"])
    message = st.text_area("Enter Message to Hide")
    password = st.text_input("Enter Password", type="password")

    if st.button("Encode"):
        if uploaded_image and message and password:
            try:
                # Open and convert image
                img = Image.open(uploaded_image)
                img = convertToRGB(img)

                # Encrypt message
                full_message = headerText + message
                encrypted = encrypt(password.encode(), full_message.encode())
                final_message = headerText + encrypted

                # Save to temp file
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    encoded_file = encodeImage(img.copy(), final_message, filename=tmp.name)
                    tmp.seek(0)
                    b64 = base64.b64encode(tmp.read()).decode()
                    href = f'<a href="data:file/png;base64,{b64}" download="encoded_image.png">📥 Download Encoded Image</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    st.success("✅ Message successfully encoded into image!")

            except Exception as e:
                st.error(f"❌ Error: {e}")
        else:
            st.warning("Please upload an image, enter a message, and provide a password.")

elif mode == "Decode":
    stego_image = st.file_uploader("Upload Stego Image", type=["png"])
    password = st.text_input("Enter Password to Decrypt", type="password")

    if st.button("Decode"):
        if stego_image and password:
            try:
                img = Image.open(stego_image)
                decoded_data = decodeImage(img)

                if not decoded_data.startswith(headerText):
                    st.error("❌ No valid hidden message found or wrong password.")
                else:
                    encrypted_msg = decoded_data[len(headerText):]
                    decrypted = decrypt(password.encode(), encrypted_msg)
                    final_msg = decrypted.decode("utf-8")[len(headerText):]
                    st.success("✅ Decoded Message:")
                    st.code(final_msg)

            except Exception as e:
                st.error(f"❌ Error: {e}")
        else:
            st.warning("Please upload a stego image and enter the correct password.")
