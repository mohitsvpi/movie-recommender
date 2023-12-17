import google.generativeai as genai
import os
from dotenv import load_dotenv
import streamlit as st
import requests

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-pro")

messages = []

def gemini_function_calling(message, messages):
    messages.append(message)

    data = {
        "contents" : [messages],
        "tools" : [
            {
                "function_declarations" : [
                    {
                        "name" : "get_movie_title",
                        "description" : "Extract the move title from the content",
                        "parameters" : {
                            "type" : "object",
                            "properties" : {
                                "title" : {
                                    "type" : "string",
                                    "description" : "Movie title without year or serial number"
                                }
                            }
                        }
                    }
                ]
            }
        ]
    }

    response = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={os.getenv('GOOGLE_API_KEY')}", json=data)

    if response.status_code != 200:
        print("ERROR : Unable to make request")
        
    response = response.json()

    if "content" not in response["candidates"][0]:
        print("ERROR: No content in response")

    message = response["candidates"][0]["content"]["parts"]

    if "functionCall" in message[0]:
        print(message[0])
        function_response = message[0]["functionCall"]["args"]
        return function_response["title"]


def get_movie_details(title):
    response = requests.get(f"https://www.omdbapi.com/?t={title}&apikey={os.getenv('MOVIE_API_KEY')}")

    if response.status_code != 200:
        print("ERROR : Unable to make request")
        
    response = response.json()

    return response

st.title("Movie Recommender")

input = st.text_input(" ", placeholder="Suggest me a popular movie from 2000's")

prompt = "Act as a movie recommendation app. Only suggest one movies out of possible multiple movie with its title and if the user ask for someother query just return please ask questions related to movies only"

if input:
    response = model.generate_content(prompt + "\n" + input)

    ai_message = {
        "role" : "user",
        "parts" : [
            {
                "text" : response.text
            }
        ]
    }

    title = gemini_function_calling(ai_message, messages=[])
    movie = get_movie_details(title)

    if title:
        movie = get_movie_details(title)
        if movie and "Error" not in movie:
            st.image(movie["Poster"], width=200)
            st.header(movie["Title"])
            st.write(movie["Plot"])
        else:
            st.write(response.text)
    else:
        st.write(response.text)


