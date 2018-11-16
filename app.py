# pip modules
import praw
from dotenv import load_dotenv
import twitter

# native modules
import pprint
import re
import os
import requests
import datetime

load_dotenv()

reddit = praw.Reddit(client_id=os.getenv('REDDIT_CLIENT_ID'),
                     client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                     user_agent=os.getenv('REDDIT_USER_AGENT'),
                     password=os.getenv('REDDIT_PASSWORD'),
                     username=os.getenv('REDDIT_USERNAME'))

twitter = twitter.Api(consumer_key=os.getenv('TWITTER_CONSUMER_KEY'),
                      consumer_secret=os.getenv('TWITTER_CONSUMER_SECRET'),
                      access_token_key=os.getenv('TWITTER_ACCESS_TOKEN_KEY'),
                      access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'))

twitter_regex = r"(status\/)(\d*)"
url_regex = r"(?:(?:https?|ftp|file):\/\/|www\.|ftp\.)(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)" \
            r"|[-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[A-Z0-9+&@#\/%=~_|$])"

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


def submission_loop():
    for submission in subreddits.stream.submissions():
        today = datetime.datetime.now()
        created_utc = datetime.datetime.utcfromtimestamp(submission.created_utc)
        age_timedelta = (today - created_utc)
        age_of_post = age_timedelta.total_seconds() / 60 / 60 / 24
        # don't comment if the post is older than 30 days. Prevents TOO OLD exception
        if age_of_post >= 30:
            continue
        # check url for supported domains (twitter)
        title_media_url = None
        if submission.domain == "twitter.com":
            # get the tweet_id from the url
            matches = re.search(twitter_regex, submission.url, re.IGNORECASE)
            tweet_id = matches[2]
            # get the video url from the tweet
            media = twitter.GetStatus(tweet_id).media
            if media:
                for item in media:
                    if item and item.type == 'video':
                        title_media_url = get_highest_bitrate(item.video_info['variants'])['url']
        # check selftext for urls
        matches = re.findall(url_regex, submission.selftext, re.IGNORECASE | re.MULTILINE)
        if title_media_url:
            print("Title: {}\nURLs: {}".format(submission.title, title_media_url))
            shortcode = upload_streamable(title_media_url)
            streamable_url = 'https://streamable.com/{}'.format(shortcode)
            comment_text = construct_comment(submission.title, streamable_url)
            submission.reply(comment_text)
            print("Commented on: {}".format(submission.title))
        # if matches:
        #     print("Title: {}\nURLs: {}".format(submission.title, matches))
        #     for match in matches:
        #         shortcode = upload_streamable(match)
        #         streamable_url = 'https://streamable.com/{}'.format(shortcode)
        #         print(streamable_url)
        #         comment_text = construct_comment(submission.title, streamable_url)
        #         submission.reply(comment_text)


def upload_streamable(url):
    res = requests.get('https://api.streamable.com/import?url={}'.format(url),
                       auth=(os.getenv('STREAMABLE_EMAIL'), os.getenv('STREAMABLE_PASSWORD')))
    # streamable api has terrible error handling.
    # Instead of using a different status for an error, they just omit that key and add a different key for each error.
    if 'status' in res.json():
        if res.json()['status'] == 1:
            return res.json()['shortcode']
    else:
        print(res.json())


def construct_comment(title, streamable_url):
    # footer = '___  \n^This ^message ^was ^created ^by ^a ^bot  \n[Request Mirror](https://www.reddit.com/message/compose?to=twittertostreamable&subject=Request%20mirror&message=Enter%20your%20urls%20here.%20It%20can%20take%20up%20to%202%20minutes%20before%20you%20receive%20a%20reply.) | [Creator](https://www.reddit.com/user/eRodY/) | [v2.0.0](https://github.com/Erody/twitter-to-streamable)'
    footer = "___  \n^This ^message ^was ^created ^by ^a ^bot  \nI'm back! | [Creator](https://www.reddit.com/user/eRodY/) | [v2.0.0](https://github.com/Erody/TwitterToStreamable_python)"
    head = '**[Mirror - {}]({})**  \n{}'.format(title, streamable_url, footer)
    return head


if __name__ == '__main__':
    submission_loop()
