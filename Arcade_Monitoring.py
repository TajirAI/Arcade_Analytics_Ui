import streamlit as st
import zipfile
import os
import pandas as pd
from datetime import datetime
import shutil
from PIL import Image
import json

DATABASE_FOLDER = "database"

os.makedirs(DATABASE_FOLDER, exist_ok=True)

game_files = ["3D ThrillMax.json", "Forza.json", "MetaVR.json", "Need_For_Speed.json", "users.json"]

for game_file in game_files:
    file_path = os.path.join(DATABASE_FOLDER, game_file)
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump([], f)

def read_json(file_name):
    file_path = os.path.join(DATABASE_FOLDER, file_name)
    with open(file_path, "r") as f:
        return json.load(f)

def write_json(file_name, data):
    file_path = os.path.join(DATABASE_FOLDER, file_name)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def write_new_json(file_name, data):
    file_path = os.path.join(DATABASE_FOLDER, file_name)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    
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

def check_screenshot(screenshot_path,save_folder,game_data,):
    if screenshot_path:
        # Get the file name from the path
        screenshot_filename = os.path.basename(screenshot_path)

        if not os.path.exists(save_folder):
                os.makedirs(save_folder)  # Create folder if it doesn't exist
            
        save_path = os.path.join(save_folder, screenshot_filename)

        for item in game_data:
            if item["screenshot"] == save_path:
                return False
        return True 
    
def check_screenshot_1(screenshot_path,save_folder,review_data,):
    if screenshot_path:
        # Get the file name from the path
        screenshot_filename = os.path.basename(screenshot_path)

        if not os.path.exists(save_folder):
                os.makedirs(save_folder)  # Create folder if it doesn't exist
            
        save_path = os.path.join(save_folder, screenshot_filename)

        for item in review_data:
            if item["screenshot"] == save_path:
                return False
        return True 

def get_game_count(game_name, selected_date):
    data = read_json(f"{game_name}.json")
    formatted_date = selected_date.strftime("%d_%m_%y")
    return len([entry for entry in data if entry["date"] == formatted_date])

def format_username(username):
    if "@" in username:
        return username.split("@")[0]  # Strip the domain
    return username
  
users = [
        {"username":"Admin","password":"1234","role":"Owner"},
        {"username":"Rizwan@tajirai.com","password":"123456","role":"Owner"},
        {"username":"Niaz@tajirai.com","password":"12345","role":"Salesman"},
        {"username":"Shahzaib@tajirai.com","password":"12345","role":"Salesman"},
    ]

if not any(user["username"] == "Admin" for user in users):
    users.append({"username": "Admin", "password": "1234", "role": "Owner"})
    # write_json("users.json", users)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    st.session_state["username"] = None

def login(username, password):
    user = next((u for u in users if u["username"] == username and u["password"] == password), None)
    if user:
        st.session_state["logged_in"] = True
        st.session_state["role"] = user["role"]
        st.session_state["username"] = user["username"]
        st.session_state["page"] = "Home" if user["role"] == "Owner" else "Data Insertion"
        st.rerun()
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
            # Read existing users from the JSON file
            # users_file = "users.json"
            # users = read_json(users_file)

            # Check if the username already exists
            if any(user["username"] == new_username for user in users):
                st.warning("Username already exists.")
            else:
                # Add the new user to the list
                new_user = {
                    "username": new_username,
                    "password": new_password,
                    "role": new_role
                }
                users.append(new_user)

                # Write updated users back to the JSON file
                # write_json(users_file, users)
                st.success("User created successfully!")
        else:
            st.warning("Only 'Owner' role can access this page.")

def convert_to_12_hour_format(hour):
    """
    Convert a 24-hour format hour to 12-hour format with AM/PM.
    
    Args:
        hour (str): Hour in 24-hour format as a string (e.g., "13:30").
    
    Returns:
        str: Time in 12-hour format with AM/PM (e.g., "01:30 PM").
    """
    try:
        # Parse the input hour as a datetime object
        from datetime import datetime
        hour = hour -1
        hour = str(hour)
        time_obj = datetime.strptime(hour, "%H")
        # Convert to 12-hour format
        return time_obj.strftime("%I %p").lstrip("0")
    except ValueError:
        # Return original hour if parsing fails
        return hour

if not st.session_state["logged_in"]:
    show_login_page()
    
else:
    st.set_page_config(layout="wide")

    with st.sidebar:
        # Display the formatted username in the sidebar
        formatted_username = format_username(st.session_state['username'])
        st.sidebar.markdown(f"""
            <div style="text-align: center;background-color: rgb(239 239 239); color:black; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);">
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
            if st.button("Review"):
                set_page("Review_Admin")
        else:
            if st.button("Data Insertion"):
                set_page("Data Insertion")
            if st.button("Review"):
                set_page("Review")

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
        selected_date = st.date_input("Select a date", None, key="home_date_input")

        if selected_date:
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
        
        game_list = ["All", "Forza", "Need_For_Speed", "3D ThrillMax", "MetaVR"]
        selected_game = st.selectbox("Select a game", game_list)
        selected_date = st.date_input("Select a date", None, key="date_input")
        
        if selected_game and selected_date:
            formatted_date = selected_date.strftime("%d_%m_%y")
            
            games_to_check = game_list[1:] if selected_game == "All" else [selected_game]
            all_filtered_data = []
            
            for game in games_to_check:
                game_data = read_json(f"{game}.json")
                filtered_data = [entry for entry in game_data if entry["date"] == formatted_date]
                
                if filtered_data:
                    for data in filtered_data:
                        data["game"] = game  # Add game name for display
                    all_filtered_data.extend(filtered_data)
            
            record_count = len(all_filtered_data)
            st.subheader(f"Total Records: {record_count} entries found")
            
            if all_filtered_data:
                for data in all_filtered_data:
                    hour_12 = (data["processing_hour"] - 1) % 24
                    am_pm = "AM" if hour_12 < 12 else "PM"
                    hour_12 = hour_12 if hour_12 <= 12 else hour_12 - 12
                    formatted_time = f"{hour_12}:00 {am_pm}"
                    
                    st.subheader(f"Details for {data['game']} on {formatted_date}")
                    st.write(f"**Time Duration:** {data['time_duration']} minutes")
                    st.write(f"**Hour:** {formatted_time}")
                    
                    if data.get("screenshot"):
                        try:
                            img = Image.open(data["screenshot"])
                            img = img.resize((400, int(400 * img.height / img.width)))
                            st.image(img, caption="Screenshot", use_container_width=False)
                        except Exception as e:
                            st.warning(f"Could not load screenshot. Error: {e}")
                    else:
                        st.write("No screenshot available")
            else:
                st.write(f"No data found for the selected date: {formatted_date}")
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

                # Read the game data from the corresponding JSON file
                game_data = read_json(f"{game_name}.json")
                games_data = []

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
                                    review_data = read_json("Review.json")  
                                    review_trash = read_json("Review_Trash.json")  
                                    review_admin = read_json("Review_Admin.json")  
                                    if check_screenshot(full_screenshot_path,save_folder,game_data):
                                        if check_screenshot_1(full_screenshot_path,save_folder,review_data): 
                                            if check_screenshot_1(full_screenshot_path,save_folder,review_trash):
                                                if check_screenshot_1(full_screenshot_path,save_folder,review_admin):             
                                                    saved_screenshot_path = save_and_display_screenshot(full_screenshot_path, save_folder)

                                                    document = {
                                                        "Game":game_name,
                                                        "processing_hour": processing_hour,
                                                        "time_duration": row["Time (minutes)"],
                                                        "screenshot": saved_screenshot_path if saved_screenshot_path else "",
                                                        "date": formatted_date,
                                                        "flag": "uncheck",
                                                        "review":"Nothing"
                                                    }

                                                    # Add the new data to the game data
                                                    games_data.append(document)
                                                else:
                                                    st.warning("Data already exists in admin review phase!")
                                            else:
                                                st.warning("Data already exists in review trash!")
                                        else:
                                            st.warning("Data already exists in review phase!")
                                    else:
                                        st.warning("Data already exists in Games!")

                review_data = read_json("Review.json")  

                for data in games_data:             
                    review_data.append(data)
                # Write the updated game data back to the JSON file
                write_json(f"Review.json", review_data)

            st.success(f"Data upload process completed for {file_count} file(s)!")
    
    elif st.session_state.get("page") == "Review":
        st.header("Review Game Activity Data")
        # Load data from Review.json
        review_data = read_json("Review.json")

        if review_data:
            # Convert data into a DataFrame
            try:
                df = pd.DataFrame(review_data)
            except ValueError:
                st.error("Invalid data format in Review.json.")
                df = pd.DataFrame()

            if not df.empty:
                # Ensure the "flag" column exists
                if "flag" not in df.columns:
                    df["flag"] = "uncheck"

                # Filter by date
                unique_dates = df['date'].dropna().unique()
                options = ["--Select Date--"] + list(unique_dates)
                selected_date = st.selectbox("Select a Date to Review", options=options)

                if selected_date != "--Select Date--":
                    # Filter data based on selected date
                    filtered_data = df[df['date'] == selected_date]

                    if not filtered_data.empty:
                        # st.subheader("Game Activity Entries")

                        if "processing_hour" in filtered_data.columns:
                            # Sort the DataFrame by the numeric value of processing_hour in ascending order
                            filtered_data = filtered_data.sort_values(by="processing_hour")

                        for i, row in filtered_data.iterrows():

                            cols = st.columns([1.5, 1.5, 0.5, 0.75, ])  # Define column layout for each row
                            converted_hour = convert_to_12_hour_format(row["processing_hour"])
                            game_info_html = f"""
                            <div style="
                                border: 1px solid #777;
                                border-radius: 5px;
                                padding: 10px;
                                font-size: 16px;
                                line-height: 1.5;
                                margin-bottom: 20px;
                            ">
                                <h5 style="line-height: 1.5;padding:0px;">Game:{row['Game']}</h5>
                                <b>Played Hour:</b> {converted_hour}<br>
                                <b>Played Time:</b> {row['time_duration']} Mins<br>
                            </div>
                            """
                            cols[0].markdown(game_info_html, unsafe_allow_html=True)
                            # Display screenshot if it exists
                            screenshot_path = row.get("screenshot", "")
                            if os.path.exists(screenshot_path):
                                image = Image.open(screenshot_path)
                                new_image = image.resize((600, 300))
                                cols[1].image(new_image, use_container_width= True)
                            else:
                                cols[1].write("Image not found.")

                            # Checkbox to toggle "flag" status
                            is_checked = row["flag"] == "uncheck"
                            checked = cols[2].checkbox("Checked", value=is_checked, key=f"check_{i}")
                            df.at[i, "flag"] = "uncheck" if checked else "Checked"

                            # Conditionally render the select box
                            if not checked:  # Show select box only if unchecked
                                selected_option = cols[3].selectbox(
                                    "Review Options",
                                    ["No person", "Salesman Detection", "Doubling", "Others"],
                                    key=f"select_{i}",
                                    label_visibility="collapsed"
                                )
                                df.at[i, "review"] = selected_option
                            else:
                                df.at[i, "review"] = "Nothing"
                                cols[3].write("")  # Leave empty space if checked

                        # Save changes to the JSON file
                        if st.button("Save Changes"):
                            # Update the Review.json with the modified DataFrame
                            review_data = df.to_dict(orient="records")
                            for data in review_data:
                                game_data = read_json(f"{data['Game']}.json")
                                review_admin_data = read_json(f"Review_Admin.json")
                                if data["flag"] == "Checked":
                                    review_admin_data.append(data)
                                    write_new_json("Review_Admin.json", review_admin_data)
                                else:
                                    game_data.append(data)
                                    write_new_json(f"{data['Game']}.json", game_data)

                            review_data = read_json("Review.json")
                            
                            remaining_data = [entry for entry in review_data if entry["date"] != selected_date]

                            # Save the remaining data back to Review.json
                            write_json("Review.json", remaining_data)
                            st.rerun()
                                    
                            st.success("Changes saved successfully!")
                    else:
                        st.info("No data available for the selected date.")
            else:
                st.warning("No valid data available in Review.json.")
        else:
            st.warning("No review data found.")

    elif st.session_state.get("page") == "Review_Admin":
        st.header("Review Game Activity Data")
        
        # Load data from Review_Admin.json
        review_data = read_json("Review_Admin.json")

        if review_data:
            # Convert data into a DataFrame
            try:
                df = pd.DataFrame(review_data)
            except ValueError:
                st.error("Invalid data format in Review_Admin.json.")
                df = pd.DataFrame()

            if not df.empty:
                # Filter by date
                unique_dates = df['date'].dropna().unique().tolist()
                unique_dates.insert(0, "--Select Date--")
                selected_date = st.selectbox("Select a Date to Review", options=unique_dates)

                # Filter data based on the selected date
                if selected_date != "--Select Date--":
                    filtered_data = df[df['date'] == selected_date]

                    if not filtered_data.empty:
                        # st.subheader("Game Activity Entries")

                        # Initialize session state for rows if not already present
                        if "row_reviews" not in st.session_state:
                            st.session_state["row_reviews"] = {}

                        for i, row in filtered_data.iterrows():
                            cols = st.columns([1.0, 0.7, 0.5],)  # Row layout

                            # Get the current review status
                            row_index = row.name
                            current_review = st.session_state["row_reviews"].get(row_index, row["review"])
                            converted_hour = convert_to_12_hour_format(row["processing_hour"])
                            
                            game_info_html = f"""
                            <div style="
                                border: 1px solid #777;
                                border-radius: 5px;
                                padding: 10px;
                                font-size: 16px;
                                line-height: 1.5;
                                margin-bottom: 20px;
                            ">
                                <h5 style="line-height: 1.5;padding:0px;">Review: {current_review}</h5>
                                <b>Game:</b> {row['Game']}<br>
                                <b>Played Hour:</b> {converted_hour}<br>
                                <b>Played Time:</b> {row['time_duration']} Mins<br>
                            </div>
                            """
                            
                            # Display the formatted HTML in the first column
                            cols[0].markdown(game_info_html, unsafe_allow_html=True)
                            # Display the screenshot if available
                            screenshot_path = row.get("screenshot", "")
                            if os.path.exists(screenshot_path):
                                image = Image.open(screenshot_path)
                                cols[1].image(image, use_container_width=True)
                            else:
                                cols[1].write("Image not found.")

                            # Button to update the review to "Noted"
                            if cols[2].button("Select!", key=f"btn_{i}"):
                                # Update session state to track changes
                                st.session_state["row_reviews"][row_index] = "Noted"
                                # Force a rerun to reflect updates
                                st.rerun()

                        # Save changes to JSON when "Save Changes" button is clicked
                        if st.button("Save Changes"):
                            # Apply the changes stored in session state to the DataFrame
                            for row_index, updated_review in st.session_state["row_reviews"].items():
                                df.at[row_index, "review"] = updated_review

                            # Convert the updated DataFrame to a dictionary and save it to JSON
                            updated_reviews = df.to_dict(orient="records")
                            print("updated_reviews",updated_reviews)
                            for data in updated_reviews:
                                game_data = read_json(f"{data['Game']}.json")
                                review_trash = read_json(f"Review_Trash.json")
                                if data["review"] == "Noted":
                                    game_data.append(data)
                                    write_new_json(f"{data['Game']}.json", game_data)
                                else:
                                    review_trash.append(data)
                                    write_new_json(f"Review_Trash.json", review_trash)

                            # Remove entries from Review_Admin.json that were processed
                            remaining_data = [entry for entry in updated_reviews if entry["date"] != selected_date]
                            write_json("Review_Admin.json", remaining_data)

                            st.success("Changes saved successfully!")
                            st.rerun()

                    else:
                        st.info("No data available for the selected date.")
                else:
                    st.info("Please select a date to review.")
            else:
                st.warning("No valid data available in Review_Admin.json.")
        else:
            st.warning("No review data found.")
