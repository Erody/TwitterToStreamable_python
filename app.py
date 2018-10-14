# pip modules
import praw
import bs4

# native modules
import pprint
import re

# local modules
import credentials

reddit = praw.Reddit(client_id=credentials.reddit['client_id'],
                     client_secret=credentials.reddit['client_secret'],
                     user_agent=credentials.reddit['user_agent'],
                     password=credentials.reddit['password'],
                     username=credentials.reddit['username'])

# subreddits = reddit.subreddit('soccer+nba')
subreddits = reddit.subreddit('testingMyBotsAndStuff')

pp = pprint.PrettyPrinter(indent=4)

for submission in subreddits.stream.submissions():
    # check url for supported domains (twitter)
    if submission.domain == "twitter.com":
        print(submission.url)
    # check selftext for urls
    regex = r"(?:(?:https?|ftp|file):\/\/|www\.|ftp\.)(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[A-Z0-9+&@#\/%=~_|$])"
    matches = re.findall(regex, submission.selftext, re.IGNORECASE | re.MULTILINE)
    if matches:
        print(submission.title, matches)

