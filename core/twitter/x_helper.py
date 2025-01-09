import asyncio
import os
import random

import pytz
import tweepy
import functools

from dotenv import load_dotenv
from datetime import datetime, timedelta

from twitter_prompts import *
from utils.llama_hf import AsyncTextGenerator

load_dotenv()
client = tweepy.Client(
    consumer_key=os.getenv('TWITTER_API_KEY'),
    consumer_secret=os.getenv('TWITTER_API_SECRET_KEY'),
    access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
    access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
)

def get_est_hour():
    utc_now = datetime.now(pytz.utc)
    est_now = utc_now.astimezone(pytz.timezone('US/Eastern'))
    return est_now.hour

def get_random_prompt(category):
    return random.choice(tweet_prompts[category])

def x(hour):
    categories = {
        "morning": ["ai_agents", "engagement"],
        "afternoon": ["memecoins", "humor"],
        "evening": ["crypto", "engagement"],
        "night": ["NFTs", "Solana"]
    }

    if 6 <= hour < 12:
        return random.choice(categories["morning"])
    elif 12 <= hour < 17:
        return random.choice(categories["afternoon"])
    elif 17 <= hour < 22:
        return random.choice(categories["evening"])
    else:
        return random.choice(categories["night"])

def init_llama(model_name="meta-llama/Llama-3.1-8B-Instruct"):
    print("Initializing neural system...")
    return AsyncTextGenerator(model_name)


def generate_tweet(base_prompt):
    current_est_time_hour = get_est_hour()
    category = get_next_category(current_est_time_hour)
    category_item_prompt = get_random_prompt(category)
    generator = init_llama()

    print(f"prompt: {category_item_prompt}\n")
    response = asyncio.run(generator.generate_text(base_prompt + category_item_prompt))

    print(f"original tweet: {response}\n")

    if len(response.response) > 280:
        response = asyncio.run(
            generator.generate_text("Shorten this to 280 characters, it is crucial that you keep the writing style: " + response.response)
        )
        print(f"shortened tweet: {response}\n")

    return response

def post_tweet(base_prompt):
    try:
        tweet = generate_tweet(base_prompt).response
        client.create_tweet(text=tweet)
        print(f"Posted tweet at {datetime.now()}: {tweet}")
    except Exception as e:
        print(f"Error posting tweet: {e}\n")


if __name__ == "__main__":
    post_tweet(BASE_PROMPT)


