# pip modules
import praw
from dotenv import load_dotenv
import twitter
import bs4

# native modules
import pprint
import re
import os

# local modules
import credentials

load_dotenv()

reddit = praw.Reddit(client_id=credentials.reddit['client_id'],
                     client_secret=credentials.reddit['client_secret'],
                     user_agent=credentials.reddit['user_agent'],
                     password=credentials.reddit['password'],
                     username=credentials.reddit['username'])

twitter = twitter.Api(consumer_key=os.getenv('TWITTER_CONSUMER_KEY'),
                      consumer_secret=os.getenv('TWITTER_CONSUMER_SECRET'),
                      access_token_key=os.getenv('TWITTER_ACCESS_TOKEN_KEY'),
                      access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'))

twitter_regex = r"(status\/)(\d*)"

# subreddits = reddit.subreddit('soccer+nba')
subreddits = reddit.subreddit('testingMyBotsAndStuff')

pp = pprint.PrettyPrinter(indent=4)


# get the video with the highest bitrate
def get_highest_bitrate(videos):
    highest_bitrate = {'bitrate': 0}
    for video in videos:
        if 'bitrate' in video:
            if video['bitrate'] > highest_bitrate['bitrate']:
                highest_bitrate = video

    return highest_bitrate

for submission in subreddits.stream.submissions():
    # check url for supported domains (twitter)
    if submission.domain == "twitter.com":
        # get the tweet_id from the url
        matches = re.search(twitter_regex, submission.url, re.IGNORECASE)
        tweet_id = matches[2]
        # get the video url from the tweet
        media = twitter.GetStatus(tweet_id).media
        if media:
            for item in media:
                if item and item.type == 'video':
                    url = get_highest_bitrate(item.video_info['variants'])['url']
                    print(url)
    # check selftext for urls
    url_regex = r"(?:(?:https?|ftp|file):\/\/|www\.|ftp\.)(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[A-Z0-9+&@#\/%=~_|$])"
    matches = re.findall(url_regex, submission.selftext, re.IGNORECASE | re.MULTILINE)
    if matches:
        print(submission.title, matches)

