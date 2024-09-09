import streamlit as st
from pymongo import MongoClient
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file located outside the project directory
dotenv_path = '../.env'  # Update this path to the location of your .env file
load_dotenv(dotenv_path=dotenv_path)

# Fetch credentials from environment variables
ADMIN_USERNAME = "Satyam"
ADMIN_PASSWORD = "12345"
client = MongoClient('mongodb+srv://bingemovies:CWuhFDboOssypOfD@binge.qvrdf.mongodb.net/')

# Set the page configuration
st.set_page_config(
    page_title="Binge+ Admin Panel",
    page_icon=":movie_camera:",
)

st.markdown("""
    <style>
    .stTextInput, .stTextArea {
        padding: 10px;
        font-size: 16px;
        border-radius: 10px;
    }
    .stButton {
        display: flex-center;
        jusitfy-content: center;
        align-items: center;
        padding: 10px;
        background-color: #f63366;
        color: white;
        border-radius: 10px;
        font-weight: bold;
        margin: 10px 0;
    }
    .stform {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

def calculate_checksum(data):
    return hash(json.dumps(data, sort_keys=True))

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False


# Sidebar for navigation
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", ["Home","Add Movie Data", "Add Series Data"])

def home():
    st.title("Welcome to Binge+ Admin Panel")
    st.write("Please select an option from the sidebar")

if not st.session_state.authenticated:
    st.title("Admin Login")
    with st.form(key='login_form'):
        username = st.text_input("Username", placeholder="Enter your username", help="Admin username required")
        password = st.text_input("Password", type='password', placeholder="Enter your password", help="Admin password required")
        login_button = st.form_submit_button("Login")

    if login_button:
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            st.success("Welcome to the admin panel!")
            st.rerun()
        else:
            st.error("Invalid username or password. Please try again.")
else:
    # Logic for navigating to different pages
    if selection == "Home":
        # Display the home page
        home()

    elif selection == "Add Movie Data":
        db = client['BINGE']
        collection = db['movies']
        
        json_file_path = 'movie_template.json'
        checksum_file_path = 'previous_checksum.txt'
        details_default = "720p | 1080p"
        
        st.title("🎬 Movie Data Submission Form")
        st.subheader("Add new movies to the Binge Movie Collection")
        st.markdown("---")  # Add a horizontal divider for cleaner UI

        # Use columns for better structure
        col1, col2 = st.columns(2)

        with st.form(key='movie_form'):
            with col1:
                title = st.text_input("🎥 Movie Title", placeholder="Enter the movie title", help="This will be the movie's title.")
                description = st.text_area("📝 Description", placeholder="Enter movie description", help="Brief description of the movie.")
                details = st.text_input("Details", value=details_default, disabled=True)
                release_date = st.text_input("📅 Release Date", placeholder="Enter release date (e.g., 25-08-2024)", help="Movie release date.")

                
            with col2:
                genre = st.text_input("🎭 Genre", placeholder="Enter genre (e.g., Action, Comedy)", help="The genre of the movie.")
                rating = st.text_input("⭐ Rating", placeholder="e.g., 8.5/10", help="Enter movie rating (e.g., IMDb rating).")
                director = st.text_input("🎬 Director", placeholder="Enter the director's name", help="Name of the director.")
                cast = st.text_area("🎭 Cast (comma separated)", placeholder="Enter cast members separated by commas", help="Enter at least 3 cast members.")

            # Remaining fields
            Image = st.text_input("🔗 Movie Poster URL", placeholder="Enter the URL of the movie poster", help="URL of the poster image.")
            visit_movie = st.text_input("🔗 Movie Link", placeholder="URL to watch the movie", help="Link to stream the movie.")
            trailer = st.text_input("🔗 Trailer Link", placeholder="Enter the URL of the movie trailer.", help="Link to the movie trailer.")

            
            
            # Submit button with a progress bar after submission
            c1,c2,c3,c4 = st.columns(4)
            with c1:
                submit_button = st.form_submit_button("Submit Movie")
            

            if submit_button:
                # Convert cast input to list
                cast_list = [member.strip() for member in cast.split(',') if member.strip()]
                if len(cast_list) < 3:
                    st.error("Please provide at least three cast members.")
                else:
                    # Load JSON Template
                    if os.path.exists(json_file_path):
                        with open(json_file_path, 'r') as file:
                            movie_data = json.load(file)
                    else:
                        st.error("JSON file not found.")
                        st.stop()

                    # Automatically update 'Link' based on 'Title'
                    if title:
                        movie_data['Link'] = f"movie_detail.html?title={title}"

                    # Load the Previous Checksum
                    previous_checksum = None
                    if os.path.exists(checksum_file_path):
                        with open(checksum_file_path, 'r') as file:
                            previous_checksum = file.read()

                    # Prepare Movie Data
                    movie_data.update({
                        "Title": title,
                        "Details": details_default,
                        "Description": description,
                        "Rating": rating,
                        "Image": Image,
                        "Link": movie_data['Link'],
                        "Visit_Movie": visit_movie,
                        "Trailer": trailer,
                        "ReleaseDate": release_date,
                        "Genre": genre,
                        "Director": director,
                        "Cast": cast_list
                    })

                    # Calculate Current Checksum
                    current_checksum = str(calculate_checksum(movie_data))

                    # Check if JSON Data Has Been Updated
                    if current_checksum == previous_checksum:
                        st.info("No changes were made to the JSON data.")
                    else:
                        # Validate and Insert Data into MongoDB
                        required_fields = ["Title", "Details", "Description", "Rating", "Image", "Link", "Visit_Movie", "Trailer", "ReleaseDate", "Genre", "Director", "Cast"]
                        if all(field in movie_data and movie_data[field] for field in required_fields):
                            try:
                                collection.insert_one(movie_data)
                                st.success(f"Movie '{title}' has been successfully added to the collection!")

                                # Save the Current Checksum
                                with open(checksum_file_path, 'w') as file:
                                    file.write(current_checksum)

                                # Clear JSON File (Except 'Link' and 'Details' Fields)
                                new_data = {
                                    "Title": "",
                                    "Details": details_default,
                                    "Description": "",
                                    "Rating": "",
                                    "Image": "",
                                    "Link": "movie_detail.html?title=",
                                    "Visit_Movie": "",
                                    "Trailer": "",
                                    "ReleaseDate": "",
                                    "Genre": "",
                                    "Director": "",
                                    "Cast": []
                                }
                                with open(json_file_path, 'w') as file:
                                    json.dump(new_data, file, indent=2)
                                st.info("Form reset and ready for new entries!")
                            except Exception as e:
                                st.error(f"An error occurred: {e}")
                        else:
                            st.error("Please ensure all fields are filled out correctly.")

    elif selection == "Add Series Data":
        db = client['BINGE-SERIES']
        collection = db['movies']
        
        json_file_path = 'series_template.json'
        checksum_file_path = 'previous_checksum.txt'
        details_default = "720p | 1080p"
        
        if 'episode_count' not in st.session_state:
            st.session_state['episode_count'] = 1
            
        def add_episode():
            st.session_state['episode_count'] += 1
        
        def remove_episode():
            if st.session_state['episode_count'] > 1:
                st.session_state['episode_count'] -= 1
        
        st.title("🎬 Series Data Submission Form")
        st.subheader("Add new series to the Binge Series Collection")
        st.markdown("---")
        
        # Use columns for better structure
        col1, col2 = st.columns(2)
        
        with st.form(key='series_form'):
            with col1:
                title = st.text_input("🎥 Movie Title", placeholder="Enter the series title", help="This will be the series's title.")
                description = st.text_area("📝 Description", placeholder="Enter series description", help="Brief description of the series.")
                details = st.text_input("Details", value=details_default, disabled=True)
                release_date = st.text_input("📅 Release Date", placeholder="Enter release date (e.g., 25-08-2024)", help="Series release date.")
            
            with col2:
                genre = st.text_input("🎭 Genre", placeholder="Enter genre (e.g., Action, Comedy)", help="The genre of the Series.")
                rating = st.text_input("⭐ Rating", placeholder="e.g., 8.5/10", help="Enter Series rating (e.g., IMDb rating).")
                director = st.text_input("🎬 Director", placeholder="Enter the director's name", help="Name of the director.")
                cast = st.text_area("🎭 Cast (comma separated)", placeholder="Enter cast members separated by commas", help="Enter at least 3 cast members.")
            
            # Remaining fields
            Image = st.text_input("🔗 Series Poster URL", placeholder="Enter the URL of the series poster", help="URL of the poster image.")
            trailer = st.text_input("🔗 Trailer Link", placeholder="Enter the URL of the series trailer.", help="Link to the series trailer.")
            episodes = []
            for i in range(st.session_state['episode_count']):
                episodename = st.text_input(f"🎥 Episode {i+1} Name", key=f"episode_{i}_name", placeholder="Enter the episode name", help="Name of the episode (e.g., Pilot)")
                episodelink = st.text_input(f"🔗 Episode {i+1} Link", key=f"episode_{i}" , placeholder="Enter the episode link", help="Link to the episode, This is a streaming link")
                
                ep = {
                    "EpisodeNumber": i+1,
                    "EpisodeTitle": episodename,
                    "EpisodeLink": episodelink
                }
                episodes.append(ep)
            c1,c2,c3,c4 = st.columns(4)
            with c1:
                submit_button = st.form_submit_button("Submit Movie")

        if submit_button:
            # Convert cast input to list
            cast_list = [member.strip() for member in cast.split(',') if member.strip()]
            if len(cast_list) < 3:
                st.error("Please provide at least three cast members.")
            else:
                # Load the JSON Template
                if os.path.exists(json_file_path):
                    with open(json_file_path, 'r') as file:
                        movie_data = json.load(file)
                else:
                    st.error("JSON file not found.")
                    st.stop()

                # Automatically update 'Link' based on 'Title'
                if title:
                    movie_data['Link'] = f"movie_detail.html?title={title}"

                # Load the Previous Checksum (if exists)
                previous_checksum = None
                if os.path.exists(checksum_file_path):
                    with open(checksum_file_path, 'r') as file:
                        previous_checksum = file.read()

                # Prepare Movie Data
                movie_data.update({
                    "Title": title,
                    "Details": details_default,
                    "Description": description,
                    "Rating": rating,
                    "Image": Image,
                    "Link": movie_data['Link'],
                    "Episodes": episodes,  # Add episodes to the movie data
                    "Trailer": trailer,
                    "ReleaseDate": release_date,
                    "Genre": genre,
                    "Director": director,
                    "Cast": cast_list
                })

                # Calculate Current Checksum
                current_checksum = str(calculate_checksum(movie_data))

                # Check if JSON Data Has Been Updated
                if current_checksum == previous_checksum:
                    st.info("JSON file has not been updated. No changes were made.")
                else:
                    # Validate and Insert Data into MongoDB
                    required_fields = ["Title", "Details", "Description", "Rating", "Image", "Link", "Episodes", "Trailer", "ReleaseDate", "Genre", "Director", "Cast"]
                    if all(field in movie_data and movie_data[field] for field in required_fields):
                        try:
                            collection.insert_one(movie_data)
                            st.success(f"Movie '{title}' has been added to the collection.")

                            # Save the Current Checksum
                            with open(checksum_file_path, 'w') as file:
                                file.write(current_checksum)

                            # Clear the JSON File (Except 'Link' and 'Details' Fields) with Specific Formatting
                            new_data = {
                                "Title": "",
                                "Details": details_default,
                                "Description": "",
                                "Rating": "",
                                "Image": "",
                                "Link": "movie_detail.html?title=",
                                "Episodes": [],  # Clear episodes
                                "Trailer": "",
                                "ReleaseDate": "",
                                "Genre": "",
                                "Director": "",
                                "Cast": []
                            }

                            # Manually write the JSON data with each key-value on a new line
                            with open(json_file_path, 'w') as file:
                                json.dump(new_data, file, indent=2)
                            
                            st.info("JSON file has been cleared (except 'Link' and 'Details' fields) with specific formatting after successful insertion.")
                        except Exception as e:
                            st.error(f"An error occurred: {e}")
                    else:
                        st.error("The template is not fully filled out. Please complete all the fields and try again.")

    # Add Episode button at the bottom of the form
        add, remove,p2,p3 = st.columns(4)
        with add:
            st.button('Add Episode', on_click=add_episode)
        with remove:
            st.button('Remove Episode', on_click=remove_episode)

