import tweepy
from datetime import datetime, timedelta
import re 
import os

TWITconsumer_key = os.getenv("TWITCONSUMER_KEY")
TWITconsumer_secret = os.getenv("TWITCONSUMER_SECRET")
TWITaccess_token = os.getenv("TWITACCESS_TOKEN")
TWITaccess_token_secret = os.getenv("TWITACCESS_TOKEN_SECRET")

auth = tweepy.OAuthHandler(TWITconsumer_key, TWITconsumer_secret)
auth.set_access_token(TWITaccess_token, TWITaccess_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True,
wait_on_rate_limit_notify=True)

tweets = {} # store all ids and tweets
days = 1 # set the # of 'past' days to pull tweets from, end date
today = datetime.utcnow() # get todays date
end_date = today - timedelta(days=days) # <-- set the end date
end_str = end_date.strftime('%m/%d/%Y') # set the end date as str
start = datetime.now() # set the start date 

### search hashtags ###
print('--- searching hashtags ---')
tags = ['shib']
for tag in tags: # loop through hashtags
    try:
        print(f'---> hashtag: {tag}')
        for status in tweepy.Cursor(api.search,q=tag,
                                    since=end_str,   
                                    exclude_replies=True,    
                                    lang='en', 
                                    tweet_mode='extended').items(100):
            if status.full_text is not None:
                text = status.full_text.lower()

                id_s = status.id # store the tweet id 
                date = status.created_at # store the date created 
                name = status.user.name # store the user name 
                tweets[id_s] = [date, name, text] # add elements to dict
        
    ### handle errors ###
    except tweepy.TweepError as e: 
        print("Tweepy Error: {}".format(e))

for key, val in tweets.items(): # loop through dictionary key/values
    val0, val1, val2 = val # unpack all variables 
    tags = re.findall("[#]\w+", val2) # get all words starting with '#'.
    tweets[key] = [val0, val1, val2, tags] # add elements to the dictionary

print('--- hashtags tweets ---')
print(f'tweets count: {len(tweets)}') # show tweets count

print('--- timer ---')
break1 = datetime.now()
print("Elapsed time: {0}".format(break1-start)) # show timer

tweets_res = {}
for key, val in tweets.items():
    if 'rt' not in val[2]:
        val[2] = val[2].split('http', 1)[0]
        if ':' in val[2] != None:
            val[2] = val[2].split(': ', 1)[1]
            val[2] = re.sub(r'[!@#$]', '', val[2])
            val[2] = "".join(val[2].splitlines())
            tweets_res[val[1]] = val[0], val[2]
        else:
            val[2] = re.sub(r'[!@#$]', '', val[2])
            val[2] = "".join(val[2].splitlines())
            tweets_res[val[1]] = val[0], val[2]
temp = []
res = {}
for key, val in tweets_res.items():
    if val[1][10:20] not in temp:
        temp.append(val[1][10:20])
        res[key] = val
    else:
        continue
for key, val in res.items():
    print(key)
    print(val[0])
    print(val[1])
    print('---')