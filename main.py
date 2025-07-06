# import streamlit as st
# from dotenv import load_dotenv
# import os
# import google.generativeai as genai
# from youtube_transcript_api import YouTubeTranscriptApi

# # Load environment variables from .env
# load_dotenv()
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# # Configure Gemini API
# genai.configure(api_key=GOOGLE_API_KEY)

# prompt = """You are a YouTube video summarizer. You will take the transcript text
# and summarize the entire video, providing the important points in bullet form within 250 words.
# Please provide the summary of the text given here: """

# # Get transcript from YouTube video
# def extract_transcript_details(youtube_video_url):
#     try:
#         video_id = youtube_video_url.split("v=")[1]
#         transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

#         transcript = ""
#         for i in transcript_text:
#             transcript += " " + i["text"]

#         return transcript
#     except Exception as e:
#         raise e

# # Generate summary from Gemini
# def generate_gemini_content(transcript_text, prompt):
#     # You can use gemini-pro or specify a faster variant if supported
#     model = genai.GenerativeModel("gemini-1.5-flash")  # You can also try "gemini-pro" with "flash" variant
#     response = model.generate_content(prompt + transcript_text)
#     return response.text

# # Streamlit UI
# st.title("YouTube Transcript to Detailed Notes Converter")
# youtube_link = st.text_input("Enter YouTube Video Link:")

# if youtube_link:
#     if "v=" in youtube_link:
#         video_id = youtube_link.split("v=")[1]
#         st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

# if st.button("Get Detailed Notes"):
#     if youtube_link and "v=" in youtube_link:
#         with st.spinner("Extracting transcript and generating summary..."):
#             transcript_text = extract_transcript_details(youtube_link)
#             if transcript_text:
#                 summary = generate_gemini_content(transcript_text, prompt)
#                 st.markdown("## Detailed Notes:")
#                 st.write(summary)
#     else:
#         st.error("Please enter a valid YouTube link containing 'v=' parameter.")

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# Prompt template
PROMPT_TEMPLATE = """You are a YouTube video summarizer. You will take the transcript text
and summarize the entire video, providing the important points in bullet form within 250 words.
Please provide the summary of the text given here: """

# Define FastAPI app
app = FastAPI()

# Request model
class YouTubeLink(BaseModel):
    url: str

# Extract transcript
def extract_transcript_details(youtube_video_url: str):
    try:
        video_id = youtube_video_url.split("v=")[1]
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([entry["text"] for entry in transcript_list])
        return transcript
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Generate summary
def generate_gemini_content(transcript_text: str, prompt: str):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Route to get summary
@app.post("/generate_summary")
async def generate_summary(data: YouTubeLink):
    url = data.url
    if "v=" not in url:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL format. Must contain 'v='.")
    transcript = extract_transcript_details(url)
    summary = generate_gemini_content(transcript, PROMPT_TEMPLATE)
    return {"summary": summary}
