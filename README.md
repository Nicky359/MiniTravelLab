# MiniTravelLab (24127511)

✅ MiniTravelLab – AI Itinerary Generator

A modern Streamlit application that provides a lightweight chat-like UI for generating personalized travel itineraries using Ollama LLM, with Firebase authentication, and saved itinerary history.

🚀 Features

✅ User Authentication (Login / Sign Up) via Firebase
✅ Travel Itinerary Generation using Ollama (Llama 3.x or any model)
✅ Clean Chat-style User Interface inspired by streamlit-chat
✅ Automatic history saving (Firestore)
✅ Load recent itineraries for each user
✅ Fully customizable UI
✅ Easy to deploy on Streamlit, local server, or Colab

🧰 Requirements

Python 3.9+

Streamlit

Firebase Admin SDK

Pyrebase4

Ollama Python client

Requests

All dependencies are included in requirements.txt.

⚙️ Installation

Clone the repository:

git clone https://github.com/Nicky359/MiniTravelLab.git
cd MiniTravelLab

Install dependencies:

pip install -r requirements.txt

🛠️ Customization

You can modify:

UI Layout

Theme / styling

Itinerary prompt logic

Firebase structure

Ollama model (llama3, mistral, phi3, etc.)

📁 Project Structure
MiniTravelLab/
│── app.py                # Main Streamlit app
│── requirements.txt      # Dependencies
│── README.md             # Project documentation
│── .streamlit/
│      └── secrets.toml   # Firebase configuration



