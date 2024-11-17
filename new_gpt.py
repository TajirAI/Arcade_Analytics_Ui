import streamlit as st
import zipfile
import os
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import hashlib
import shutil
from PIL import Image

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client["arcade_db"]
users_collection = db["users"]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_and_display_screenshot(screenshot_path, save_folder):
    if screenshot_path:
        try:
            # Get the file name from the path
            screenshot_filename = os.path.basename(screenshot_path)

            # Check if the directory exists, and create it if necessary
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)  # Create folder if it doesn't exist
            
            save_path = os.path.join(save_folder, screenshot_filename)

            # Ensure that the screenshot is saved to the correct folder
            img = Image.open(screenshot_path)  # Open the image using PIL
            img.save(save_path)  # Save the screenshot in the specified folder
            
            return save_path  # Return the saved path of the screenshot
        except Exception as e:
            st.warning(f"Could not save screenshot {screenshot_path}. Error: {e}")
    return None

def get_game_count(game_name, selected_date):
    collection = db[game_name]
    formatted_date = selected_date.strftime("%d_%m_%y")
    count = collection.count_documents({"date": formatted_date})
    return count

def format_username(username):
    if "@" in username:
        return username.split("@")[0]  # Strip the domain
    return username

if users_collection.count_documents({}) == 0:
    users_collection.insert_one({
        "username": "Admin",
        "password": hash_password("1234"),
        "role": "Owner"
    })

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    st.session_state["username"] = None

def login(username, password):
    user = users_collection.find_one({"username": username, "password": hash_password(password)})
    if user:
        st.session_state["logged_in"] = True
        st.session_state["role"] = user["role"]
        st.session_state["username"] = user["username"]
        
        # Set the default page based on user role
        if user["role"] == "Owner":
            st.session_state["page"] = "Home"
        else:
            st.session_state["page"] = "Data Insertion"
        
        st.rerun()
            
        return True
    return False

def logout():
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    st.session_state["username"] = None

def show_login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login(username, password):
            st.success("Logged in successfully!")
            st.session_state["page"] = "main"  # Switch to main page view
            st.rerun()
        else:
            st.error("Invalid username or password")

def set_page(page):
    st.session_state["page"] = page
    st.rerun()

def show_signup_page():
    st.title("User Signup")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    new_role = st.selectbox("Role", ["Owner", "Salesman"])
    if st.button("Create User"):
        if st.session_state["role"] == "Owner":
            if users_collection.find_one({"username": new_username}):
                st.warning("Username already exists.")
            else:
                users_collection.insert_one({
                    "username": new_username,
                    "password": hash_password(new_password),
                    "role": new_role
                })
                st.success("User created successfully!")
        else:
            st.warning("Only 'Owner' role can access this page.")

if not st.session_state["logged_in"]:
    show_login_page()
    
else:
    st.set_page_config(layout="wide")

    with st.sidebar:
        # Display the formatted username in the sidebar
        formatted_username = format_username(st.session_state['username'])
        st.sidebar.markdown(f"""
            <div style="text-align: center;background-color: rgb(22 22 22); color:white; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);">
                <h2>Welcome, {formatted_username}.</h2>
            </div>
        """, unsafe_allow_html=True)
        st.sidebar.markdown("<br>", unsafe_allow_html=True)

        if st.sidebar.button("Logout",use_container_width=True,icon=":material/logout:",):
            logout()
            st.rerun()

        # Show buttons for navigation based on user role
        if st.session_state["role"] == "Owner":
            if st.button("Home"):
                set_page("Home")
            if st.button("Briefing"):
                set_page("Briefing")
            if st.button("User Signup"):
                set_page("User Signup")
        if st.button("Data Insertion"):
            set_page("Data Insertion")

    if st.session_state.get("page") == "Home":
        # Main page content
        st.header("Day-End Performance Report")
            
        # Custom CSS for page background and card styling
        st.markdown("""
            <style>
            body {background-color: #f2f2f2;}
            .card {background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin: 10px 0; text-align: center; border: 2px solid #e0e0eb; transition: background-color 0.3s ease;}
            .card:hover {background-color: #e6f7ff; border-color: #b3e0ff;}
            .card-title {font-size: 24px; font-weight: bold; color: #333;}
            .card-text {font-size: 18px; color: #666;}
            </style>
        """, unsafe_allow_html=True)

        # Game prices (you can adjust these as needed)
        game_prices = {
            "Forza": 300,
            "Need_For_Speed": 200,
            "3D ThrillMax": 300,
            "MetaVR": 300
        }

        # Function to calculate total revenue for the selected date
        def calculate_total_revenue(selected_date):
            total_revenue = 0
            for game_name, price in game_prices.items():
                game_count = get_game_count(game_name, selected_date)
                total_revenue += game_count * price
            return total_revenue

        # Date selector for filtering data
        selected_date = st.date_input("Select a date", datetime.today())

        # Calculate and display total revenue
        total_revenue = calculate_total_revenue(selected_date)
        st.markdown(f"""
            <div class="card">
                <div class="card-title">Total Money Earned</div>
                <div class="card-text">Rs.{total_revenue}</div>
            </div>
        """, unsafe_allow_html=True)

        # Show counters for each game
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            forza_count = get_game_count("Forza", selected_date)
            st.markdown(f"""
                <div class="card">
                    <div class="card-title">Forza</div>
                    <div class="card-text">{forza_count} games played</div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            Need_For_Speed_count = get_game_count("Need_For_Speed", selected_date)
            st.markdown(f"""
                <div class="card">
                    <div class="card-title">NFS</div>
                    <div class="card-text">{Need_For_Speed_count} games played</div>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            thrillmax_count = get_game_count("3D ThrillMax", selected_date)
            st.markdown(f"""
                <div class="card">
                    <div class="card-title">3D ThrillMax</div>
                    <div class="card-text">{thrillmax_count} games played</div>
                </div>
            """, unsafe_allow_html=True)
        with col4:
            MetaVR_count = get_game_count("MetaVR", selected_date)
            st.markdown(f"""
                <div class="card">
                    <div class="card-title">MetaVR</div>
                    <div class="card-text">{MetaVR_count} games played</div>
                </div>
            """, unsafe_allow_html=True)
    
    elif st.session_state.get("page") == "Briefing":
        st.header("Game Briefing")

        game_list = ["Forza", "Need_For_Speed", "3D ThrillMax","MetaVR"]
        selected_game = st.selectbox("Select a game", game_list)
        selected_date = st.date_input("Select a date", datetime.today())

        if selected_game and selected_date:
            formatted_date = selected_date.strftime("%d_%m_%y")
            collection = db[selected_game]
            game_data = list(collection.find({"date": formatted_date}))

            record_count = len(game_data)
            st.subheader(f"Total Records: {record_count} entries found")

            if game_data:
                for data in game_data:
                    hour_12 = (data["processing_hour"] - 1) % 24
                    am_pm = "AM" if hour_12 < 12 else "PM"
                    hour_12 = hour_12 if hour_12 <= 12 else hour_12 - 12
                    formatted_time = f"{hour_12}:00 {am_pm}"

                    st.subheader(f"Details for {selected_game} on {formatted_date}")
                    st.write(f"**Time Duration:** {data['time_duration']} minutes")
                    st.write(f"**Hour:** {formatted_time}")
                    
                    if data["screenshot"]:
                        img = Image.open(data["screenshot"])
                        img = img.resize((400, int(400 * img.height / img.width)))
                        st.image(img, caption="Screenshot", use_container_width=False)
                    else:
                        st.write("No screenshot available")
            else:
                st.write(f"No data found for {selected_game} on {formatted_date}")
        else:
            st.write("Please select both a game and a date to view the briefing details.")
    
    elif st.session_state.get("page") == "User Signup" and st.session_state["role"] == "Owner":
        # Only Owner can view the signup page
        show_signup_page()

    elif st.session_state.get("page") == "Data Insertion":
        st.header("Upload Game Activity Files")
        uploaded_zips = st.file_uploader("Upload your ZIP files", type="zip", accept_multiple_files=True)

        if uploaded_zips:
            file_count = 0  # Initialize a counter for the uploaded files
            for uploaded_zip in uploaded_zips:
                file_count += 1  # Increment the counter for each file
                zip_name = uploaded_zip.name
                zip_base_name = zip_name.replace(".zip", "")
                date_str = zip_base_name[-8:]
                game_name = zip_base_name[:-8].rstrip('_')

                try:
                    date = datetime.strptime(date_str, "%d_%m_%y").date()
                except ValueError:
                    st.error(f"The date format in the filename '{zip_name}' is incorrect. Expected format: MM_DD_YY.")
                    continue

                collection = db[game_name]
                collection.create_index("screenshot", unique=True)
                save_folder = os.path.join(os.getcwd(), 'screenshots', game_name)

                if not os.path.exists(save_folder):
                    os.makedirs(save_folder)

                extract_dir = f"/tmp/game_data_{game_name}"
                if os.path.exists(extract_dir):
                    shutil.rmtree(extract_dir)
                os.makedirs(extract_dir)

                with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)

                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        if file.endswith(".csv") and "Hour" in file:
                            try:
                                processing_hour = int(file.split("_")[0])
                            except ValueError:
                                st.warning(f"Unexpected file format for file: {file} in {zip_name}")
                                continue

                            csv_path = os.path.join(root, file)
                            if os.path.exists(csv_path):
                                data = pd.read_csv(csv_path, skiprows=1)

                                if "Time (minutes)" not in data.columns:
                                    st.warning(f"Column 'Time (minutes)' is missing in file: {file} in {zip_name}")
                                    continue

                                valid_data = data[data["Time (minutes)"].notnull()]
                                if valid_data.empty:
                                    continue

                                formatted_date = date.strftime("%d_%m_%y")

                                for _, row in valid_data.iterrows():
                                    screenshot_path = row.get("Screenshot Path", "")
                                    full_screenshot_path = os.path.join(extract_dir, screenshot_path)
                                    saved_screenshot_path = save_and_display_screenshot(full_screenshot_path, save_folder)

                                    document = {
                                        "processing_hour": processing_hour,
                                        "time_duration": row["Time (minutes)"],
                                        "screenshot": saved_screenshot_path if saved_screenshot_path else "",
                                        "date": formatted_date
                                    }

                                    try:
                                        collection.update_one(
                                            {"screenshot": document["screenshot"]},
                                            {"$setOnInsert": document},
                                            upsert=True
                                        )
                                    except Exception as e:
                                        st.warning(f"Duplicate entry for screenshot '{document['screenshot']}' in {zip_name}, skipping.")

            st.success(f"Data upload process completed for {file_count} file(s)!")

