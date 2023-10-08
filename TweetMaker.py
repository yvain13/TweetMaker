#!/home/xero0786/.virtualenvs/tweet/bin/python3.10
# Required imports
import os
import openai
import tweepy
from dotenv import load_dotenv
import requests
import io
from PIL import Image

# Load environment variables from .env file
load_dotenv()

# Setting up API endpoints and keys
hf_token = os.getenv("HF_STABILITY_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": "Bearer " + hf_token}
openai.api_key = os.getenv("OPENAI_API_KEY")

def send_tweet(tweet_text):
    # Setting up Twitter API credentials
    consumer_key = os.environ.get("TW_CONSUMER_KEY")
    consumer_secret = os.environ.get("TW_CONSUMER_SECRET")
    access_token = os.environ.get("TW_ACCESS_TOKEN")
    access_token_secret = os.environ.get("TW_ACCESS_TOKEN_SECRET")
    bearer_token = os.environ.get("TW_BEARER_TOKEN")
    
    # Authenticate to Twitter
    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )
    
    # V1 Twitter API Authentication
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    
    # Send tweet with media
    try:
        media_id = api.media_upload(filename="downloaded_image.jpg").media_id_string
        client.create_tweet(text=tweet_text, media_ids=[media_id])
        print("Tweet sent successfully!")
    except tweepy.TweepyException as e:
        print("Error sending tweet: {}".format(e.reason))

def searchQuotes():
    # Retrieve quotes related to Marcus Aurelius based on Meditation
    result = requests.post(
        "https://snow.onrender.com",
        json={"query": "Quotes by Marcus Aurelius based on Meditation"},
    ).json()
    return getQuote(result)

def getQuote(quoteSummary):
    # Extract and summarize quote using openai
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "...[message truncated for brevity]..."
            },
            {"role": "user", "content": quoteSummary},
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    
    content = response["choices"][0]["message"]["content"]
    print(content)
    return content

def getImageCaption(quote):
    # Extract image caption from the summarized quote using openai
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "...[message truncated for brevity]..."
            },
            {
                "role":"user",
                "content" : quote
            }
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    
    content = response["choices"][0]["message"]["content"]
    print(content)
    return content

def delete_file(filename):
    # Delete specified file
    try:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"'{filename}' has been deleted.")
        else:
            print(f"'{filename}' does not exist in the current directory.")
    except Exception as e:
        print(f"Error occurred: {e}")

def query(payload):
    # Query HuggingFace API to generate an image
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

# Execution starts here
quote = searchQuotes()
caption = getImageCaption(quote)

image_bytes = query(
    {
        "inputs": "...[message truncated for brevity]..."
    }
)

# Save the generated image and send a tweet
if image_bytes:
    image = Image.open(io.BytesIO(image_bytes))
    image_path = "./downloaded_image.jpg"
    image.save(image_path)
    send_tweet(quote)
    delete_file("downloaded_image.jpg")
else:
    print("Failed to download the image.")
