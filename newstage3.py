import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import os

# Step 1: Load the dataset
df = pd.read_csv("ocr.csv")

# Step 2: Set up session state to track the current row
if 'current_row' not in st.session_state:
    st.session_state.current_row = 0

# Step 3: Function to display the current image, OCR, and LaTeX preview
def display_current_data():
    current_data = df.iloc[st.session_state.current_row]

    # Display the image
    image_url = current_data["image_location"]
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))

    # Check if the image is portrait (height > width), and if so, automatically rotate it
    width, height = img.size
    if height > width:
        img = img.rotate(90, expand=True)  # Automatically rotate to landscape if portrait

    # Step 3.1: Add a slider to rotate the image
    rotation_angle = st.slider("Rotate Image", min_value=0, max_value=360, step=1, value=0)
    
    # Rotate the image based on the slider value
    img_rotated = img.rotate(rotation_angle, expand=True)
    
    # Display the rotated image
    st.image(img_rotated, caption=f"Image {st.session_state.current_row + 1} (Rotated by {rotation_angle}°)", use_column_width=True)

    # Display the OCR text (plain)
    ocr_text = current_data["gemini_1.5_pro_exp_ocr"]
    st.text_area("OCR Text (Plain)", ocr_text, height=200, disabled=True)

    # Define the permanent save directory for the .mmd file
    save_directory = "/Users/vedantaryan/Desktop/streamlitapp/saveMMd"
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)  # Create the directory if it doesn't exist

    # Save LaTeX content to a permanent .mmd file
    mmd_file_path = os.path.join(save_directory, f"ocr_latex_{st.session_state.current_row + 1}.mmd")
    
    with open(mmd_file_path, "w") as f:
        latex_content = ocr_text  # No need to wrap it in ```latex and ```

        f.write(latex_content)

    # Display LaTeX preview using st.markdown from the saved .mmd file
    st.markdown("### LaTeX Preview:")
    with open(mmd_file_path, "r") as mmd_file:
        mmd_content = mmd_file.read()
        st.markdown(mmd_content, unsafe_allow_html=True)

    # Display current correctness
    correctness = current_data["correctness"]
    st.radio("Mark the correctness", ["Correct", "Incorrect"], index=0 if correctness == "Correct" else 1, key="correctness_radio")

# Step 4: Buttons to navigate through images
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button('Previous'):
        if st.session_state.current_row > 0:
            st.session_state.current_row -= 1
            st.experimental_rerun()

with col3:
    if st.button('Next'):
        if st.session_state.current_row < len(df) - 1:
            st.session_state.current_row += 1
            st.experimental_rerun()

# Display the current data
display_current_data()

# Step 5: Save the user's feedback for correctness
if st.button("Save"):
    df.at[st.session_state.current_row, 'correctness'] = st.session_state.correctness_radio
    df.to_csv("updated_dataset.csv", index=False)  # Saving updated dataset with correctness
    st.success(f"Correctness for image {st.session_state.current_row + 1} has been saved!")
