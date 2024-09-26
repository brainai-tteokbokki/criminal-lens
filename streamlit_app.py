import base64
import os
import requests
import streamlit as st
from dotenv import load_dotenv
import src.utils as utils
load_dotenv()

SERVER_URL = os.getenv("SERVER_URL")
TEMP_DIR = os.path.join(os.getcwd(), "src", "temp_dir")

st.set_page_config(
    page_title="CriminalLens",
    page_icon=":eyeglasses:",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title(":eyeglasses: CriminalLens")

st.sidebar.header(":eyeglasses: Welcome to CriminalLens")
sel_menu = st.sidebar.radio("Select menu", ["How to use", "View criminals", "Search Criminal", "Regi Criminal", "Rate Plan", "About"])

if sel_menu == "How to use":
    st.header("How to use?")
    st.write("1. Click on 'Search' in the sidebar to search for a criminal.")
    st.write("2. Click on 'Regi Criminal' in the sidebar to register a criminal.")
    st.write("3. Click on 'About' in the sidebar to know more about the project.")
    st.write(":eyeglasses: Find it!")
    st.write("")
    st.write("")
    st.write("")
    st.write("The feature is not implemented yet ...")

elif sel_menu == "View criminals":
    submit_url = f"{SERVER_URL}/api/list"
    
    st.header("View criminals")
    # try:
    st.warning("Loading list of criminals...")
    
    res = requests.get(submit_url, timeout=10)
    res_json = res.json()
    
    if res_json.get('error', True):
        st.error(f"Loading failed: {res_json.get('detail', 'Unknown error')}")
    else:
        st.success(f"Loading successful: {res_json.get('detail', 'Unknown result')}")
        
        res_json = res_json['data']
        if res_json == []:
            st.write("No criminals registered.")
            
        else:
            crimi_layout_cell = []
            for i in range((len(res_json) + 2) // 3):
                crimi_layout_cell.append(st.columns(3))

            crimi_layout_cell = [col for row in crimi_layout_cell for col in row]

            for index, criminal in enumerate(res_json):
                crimi_layout_cell[index].write(f"Name: {criminal['crimi_name']}")
                crimi_layout_cell[index].write(f"Desc: {criminal['crimi_desc']}")
                # with open(os.path.join(TEMP_DIR, 'view_temp.jpg'), 'wb') as f:
                #     f.write(base64.b64decode(criminal['crimi_face'][0]))
                # crimi_layout_cell[index].image(os.path.join(TEMP_DIR, 'view_temp.jpg'), caption=f"Regi time: {criminal['regi_time']}", use_column_width=True)
                crimi_layout_cell[index].write("")
        
            os.remove(os.path.join(TEMP_DIR, 'view_temp.jpg'))
                
    # except Exception as e:
    #     st.error("Failed to load criminals. Are you connected to the Internet?")

elif sel_menu == "Search Criminal":
    submit_url = f"{SERVER_URL}/api/search"
    
    st.header("Search Criminal")
    
    upload_type = st.radio("Select upload type", ["Upload image", "Take a picture"])

    criminal_image = None
    if upload_type == "Upload image":
        criminal_image = st.file_uploader("Criminal image")
    else:
        picture = st.camera_input("Take a picture")
        if picture:
            st.image(picture)
            criminal_image = picture

    st.write("Uploaded photos will be deleted immediately after processing.")
    submit_button = st.button(label='Search')
    
    if submit_button:
        if criminal_image == None:
            st.error("Please upload or take a picture of the criminal.")
        else:
            st.warning("Searching...")
            
            try:
                res = requests.post(submit_url, timeout=10, files={"image": criminal_image})
                res_json = res.json()
                
                if res_json.get("error", True):
                    st.error(f"Search failed: {res_json.get("detail", "Unknown error")}")
                else:
                    st.success(f"Search successful: {res_json.get("detail", "Unknown result")}")
                    
                    similar_layout_cell = []
                    for i in range((len(res_json["similar_info"]) + 2 + 3) // 3):
                        similar_layout_cell.append(st.columns(3))
                    similar_layout_cell = [col for row in similar_layout_cell for col in row]
                    
                    suspect_layout_cell = []
                    for i in range((len(res_json["suspect_info"]) + 2 + 3) // 3):
                        suspect_layout_cell.append(st.columns(3))
                    suspect_layout_cell = [col for row in suspect_layout_cell for col in row]
                    
                    similar_layout_cell[0].header("Similar")
                    for index, criminal in enumerate(res_json["similar_info"]):
                        similar_layout_cell[index+3].write(f"Name: {criminal['crimi_name']}")
                        similar_layout_cell[index+3].write(f"Desc: {criminal['crimi_desc']}")
                        # with open(os.path.join(TEMP_DIR, 'search_temp.jpg'), 'wb') as f:
                        #     f.write(base64.b64decode(criminal['crimi_face']))
                        # similar_layout_cell[index+3].image(os.path.join(TEMP_DIR, 'search_temp.jpg'), use_column_width=True)
                        similar_layout_cell[index+3].write("")
                    
                    suspect_layout_cell[0].header("Suspect")
                    for index, criminal in enumerate(res_json["suspect_info"]):
                        suspect_layout_cell[index+3].write(f"Name: {criminal['crimi_name']}")
                        suspect_layout_cell[index+3].write(f"Desc: {criminal['crimi_desc']}")
                        # with open(os.path.join(TEMP_DIR, 'search_temp.jpg'), 'wb') as f:
                        #     f.write(base64.b64decode(criminal['crimi_face']))
                        # suspect_layout_cell[index+3].image(os.path.join(TEMP_DIR, 'search_temp.jpg'), use_column_width=True)
                        suspect_layout_cell[index+3].write("")
                    
                    os.remove(os.path.join(TEMP_DIR, 'search_temp.jpg'))
                    
            except Exception as e:
                st.error(f"Search failed. Are you connected to the Internet?")
            

elif sel_menu == "Regi Criminal":
    submit_url = f"{SERVER_URL}/api/regi"
    
    st.header("Registration Criminal")
    criminal_name = st.text_input("Criminal name")
    criminal_desc = st.text_input("Criminal Desc")
    upload_type = st.radio("Select upload type", ["Upload image", "Take a picture"])

    criminal_image = None
    if upload_type == "Upload image":
        criminal_image = st.file_uploader("Criminal image")
    else:
        picture = st.camera_input("Take a picture")
        if picture:
            st.image(picture)
            criminal_image = picture
    
    st.write("The information you upload will be stored only for processing purposes. The information you upload may be shared. Do not upload important information. We cannot be held responsible.")
    agree_ckbox = st.checkbox("I understand and agree")

    submit_button = st.button(label='Register')
    
    if submit_button:
        if not criminal_name:
            st.error("Please enter the criminal name.")
        elif not criminal_desc:
            st.error("Please enter the criminal desc.")
        elif criminal_image == None:
            st.error("Please upload or take a picture of the criminal.")
        elif not agree_ckbox:
            st.error("Please agree to the terms.")
        else:
            st.warning("Registering...")
            
            try:
                res_data = {
                    'crimi_name' : criminal_name,
                    'crimi_desc' : criminal_desc,
                    'is_agree'   : agree_ckbox,
                    'regi_time'  : utils.get_now_ftime()
                }
                res_file = {
                    'crimi_image': criminal_image
                }
                
                res = requests.post(submit_url, timeout=10, data=res_data, files=res_file)
                res_json = res.json()
                
                if res_json.get('error', True):
                    st.error(f"Registration failed: {res_json.get('detail', 'Unknown error')}")
                else:
                    st.success(f"Registration successful: {res_json.get('detail', 'Unknown result')}")
                    
            except Exception as e:
                st.error(f"Registration failed. Are you connected to the Internet?")

elif sel_menu == "Rate Plan":
    st.header("Rate Plan")
    
    col1, col2, col3 = st.columns(3)
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    col1.header("Free Plan (Basic)")
    col1.write("Cost: $0")
    col1.write("Features: Limited to 30 facial scans per day, basic recognition with lower accuracy, ads included, and slower processing times.")
    if btn_col1.button("Free"):
        st.header("You are using the free tier. Thank you!")
    
    col2.header("Premium Plan (Individual)")
    col2.write("Monthly Subscription: $5.99/month")
    col2.write("Annual Subscription: $59.90/year (2 months free)")
    col2.write("Features: Unlimited facial scans, no ads, priority processing, high-accuracy recognition, historical data tracking (e.g., previously identified individuals), and alerts for matches.")
    if btn_col2.button("Subscribe now"):
        st.header("Thank you for signing up!")
    
    col3.header("Premium Plan (Business)")
    col3.write("Monthly Subscription: $2.99/user/month. (10 users or more)")
    col3.write("Features: Provides Premium Tier (Individual) features to all users")
    if btn_col3.button("Contact Us"):
        st.header("Please feel free to contact us for consultation.\nContact email: contact@tteokbokki.com")

elif sel_menu == "About":
    st.header("About")
    st.write("CriminalLens is a project that helps you to search for criminals.")
    st.write("Are you curious? [Visit the site below](https://sites.google.com/view/teamtteokbokki)")
    st.write("")
    st.write("Rate flan detail view: [View](https://sites.google.com/view/teamtteokbokki/finance-%EC%9E%AC%EB%AC%B4?authuser=0)")
    st.write("")
    st.write("This project is developed by Team tteokbokki.")
    st.write("Are you curious about the source code? This is our [GitHub](https://github.com/brainai-tteokbokki)")
    