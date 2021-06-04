### necessary imports ### 
from flask import Flask, render_template, request
import os
import psycopg2
import pandas
from pandas import DataFrame 
from datetime import datetime, timedelta
from IPython.display import HTML
import requests
import re
from bs4 import BeautifulSoup
import tweepy


####################
### scraping new tokens from CMC html ### 
####################
print('--- scraping new tokens ---')
source_new = requests.get(f'https://coinmarketcap.com/new/').text
soup_4 = BeautifulSoup(source_new, 'lxml')
card_5 = soup_4.find('tbody')
print('--- New Release Tokens ---')
new_tokens = {}
for td in card_5.find_all('tr')[0:10]:
    token = {}
    new_num = td.select_one('td:nth-child(2)', style='text').text
    #token['release #'] = new_num
    new_name = td.select_one('td:nth-child(3)', style='text').a.div.div.p.text
    token['name'] = new_name
    new_symbol = td.select_one('td:nth-child(3)', style='text').a.div.div.div.p.text
    token['symbol'] = new_symbol
    new_img = td.select_one('td:nth-child(3)', style='text').a.div.img['src']
    token['image'] = new_img
    new_release = td.select_one('td:nth-child(10)', style='text').text
    token['release date'] = new_release
    new_price = td.select_one('td:nth-child(4)', style='text').text
    token['price'] = new_price
    new_change1hr = td.select_one('td:nth-child(5)', style='text').span.text
    token['change 1hr'] = new_change1hr
    new_change24hr = td.select_one('td:nth-child(6)', style='text').span.text
    token['change 24hr'] = new_change24hr
    new_volume = td.select_one('td:nth-child(8)', style='text').text
    token['volume'] = new_volume
    new_chain = td.select_one('td:nth-child(9)', style='text').div.text
    token['blockchain'] = new_chain
    cmc_url = td.select_one('td:nth-child(3)', style='text').a['href']
    token['cmc url'] = 'https://coinmarketcap.com' + cmc_url
    new_tokens[new_num] = token
for key, val in new_tokens.items():
    print(key)
    print(val)
    print('-----')
print('-----')
####################
### pulling token data from CMC api ###
####################
### take user input ###
user_input = input ("Enter the token name:")
# user_input = request.form['user_input']
print('--- pulling token data from api ---')
# user_input = ['xrp']
### CMC api urls ###
x_query = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
x_latest = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
x_meta = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/info'
### CMC api key ###
apikey = os.getenv("CMC_APIKEY")
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY' : apikey,
}
### parameters ###
params = {
    'symbol' : user_input,
}
####################
### CMC api token stats ###
####################
source_stats = requests.get(x_query, params=params , headers=headers).json()
coins_stats = source_stats['data']
# print(coins_stats) ##
token_info = {}
for key, value in coins_stats.items():
    name = value['name']
    token_info['name'] = name
    symbol = value['symbol']
    token_info['symbol'] = symbol
    slug = value['slug']
    token_info['slug'] = slug
    date_added = value['date_added'][:10]
    token_info['date added'] = date_added
    is_active = value['is_active']
    if is_active != 1:
        token_info['active'] = 'no'
    else:
        token_info['active'] = 'yes'
    total_supply = value['total_supply']
    token_info['total supply'] = "{:,}".format(total_supply)
    circulating_supply = value['circulating_supply']
    token_info['circulating supply'] = "{:,}".format(circulating_supply)
    market_cap = value['quote']['USD']['market_cap']        
    token_info['market cap'] = "{:,}".format(market_cap)
    price = value['quote']['USD']['price']
    token_info['price'] = "{:,}".format(price)
    volume_24h = value['quote']['USD']['volume_24h']
    token_info['volume'] = "{:,}".format(volume_24h)
    change_1h = value['quote']['USD']['percent_change_1h']
    token_info['change 1hr'] = "{:,}".format(change_1h)
    change_24h = value['quote']['USD']['percent_change_24h']
    token_info['change 24hr'] = "{:,}".format(change_24h)
    change_7d = value['quote']['USD']['percent_change_7d']
    token_info['change 7d'] = "{:,}".format(change_7d)
    change_30d = value['quote']['USD']['percent_change_30d']
    token_info['change 30d'] = "{:,}".format(change_30d)
    change_60d = value['quote']['USD']['percent_change_60d']
    token_info['change 60d'] = "{:,}".format(change_60d)
    change_90d = value['quote']['USD']['percent_change_90d']
    token_info['change 90d'] = "{:,}".format(change_90d)
    for key, val in token_info.items():
        print(f'{key}: {val}')
    ####################
    ### CMC api token urls ###
    ####################
    source_urls = requests.get(x_meta, params=params , headers=headers).json()
    coins_urls = source_urls['data']
    token_urls = []
    for key, value2 in coins_urls.items():
        if value['name'] == value2['name']:
            logo = value2['logo']
            for x in value2['urls']['explorer']:
                token_urls.append(x)
    token_info['source urls'] = token_urls
    ####################
    ### CMC html scrape token stats1 ###
    ####################
    print('--- scraping token stats ---')
    url_name = name.replace(' ', '-')
    source_stats2 = requests.get(f'https://coinmarketcap.com/currencies/{url_name}').text
    coin_stats2 = BeautifulSoup(source_stats2, 'lxml')
    # block1 = coin_stats2.find('div', class_='statsBlock___11SXA').div
    # block1_2 = block1.select_one('div:nth-child(2)')
    # marketcap_number = block1_2.div.text
    # if block1_2.span is not None:
    #     marketcap_change = block1_2.span.text
    # else:
    #     marketcap_change = 'No data'
    # print(marketcap_number) ##
    # print(marketcap_change) ##
    # token_info['market cap number'] = marketcap_number
    # token_info['market cap change'] = marketcap_change
    # print(token_info['market cap number']) ##
    # print(token_info['market cap change']) ##
    # print('-----') ##
    # ################
    # ### Volume stats ###
    # block2 = coin_stats2.find('div', class_='hide___2JmAL statsContainer___2uXZW')
    # block2_2 = block2.select_one('div:nth-child(3)')
    # change = block2_2.find('div', class_='statsItemRight___yJ5i-').span
    # volume_number = block2_2.find('div', class_='statsItemRight___yJ5i-').div.text
    # if change.span is not None:
    #     volume_change = change.text
    # else:
    #     volume_change = 'No data'
    # print(volume_number) ##
    # print(volume_change) ##
    # token_info['volume number'] = volume_number
    # token_info['volume change'] = volume_change
    # print(token_info['volume number']) ##
    # print(token_info['volume change']) ##
    # print('-----') ##
    # ################
    # ### Circulating stats ###
    # block3 = block2.select_one('div:nth-child(4)')
    # ts_2text = block3.find('div', class_='sc-16r8icm-0 kkJvVq').div.text
    # token_info['circulating_supply'] = ts_2text
    # print(token_info['circulating_supply'])
    # print(token_info['circulating supply'])
    ####################
    ### CMC html scrape token stats2 ###
    ####################
    coin_scrape_stats = coin_stats2.find('div', class_='sc-16r8icm-0 jIZLYs container___E9axz')
    body = coin_scrape_stats.find('tbody')
    ### 24hr change stats ###
    chang24r = body.select_one('tr:nth-child(3)')
    chang24r_numbers = chang24r.td.text
    token_info['24hr low / high'] = chang24r_numbers
    # print(token_info['24hr low / high']) ##
    ### Market dominance stats ###
    market_dominance = body.select_one('tr:nth-child(6)')
    market_dominance_numbers = market_dominance.td.text
    token_info['market dominance'] = market_dominance_numbers
    # print(token_info['market dominance']) ## 
    ####################
    ### CMC html scrape token hash ###
    ####################
    url_name = name.replace(' ', '-')
    token_hash = []
    hash_url = []
    platform = []
    source_hash = requests.get(f'https://coinmarketcap.com/currencies/{url_name}').text
    coins_hash = BeautifulSoup(source_hash, 'lxml')
    ### Token hash ###
    for head in coins_hash.find_all('div', class_='sc-16r8icm-0 dOJIkS container___2dCiP contractsRow'):

        if 'Con' in head.div.text:
            content = head.find('div', class_= 'content___MhX1h')
            thash = content.div.a['href']
            hash_url.append(thash)
            plat  = content.div.a.span.text
            platform.append(plat)
            if 'Eth' in plat:
                token_hash.append(thash[27:])
            else:
                token_hash.append(thash[26:])
    if len(token_hash) == 0:
        token_info['hash'] = 'No data'
        token_info['hash_url'] = 'No data'
        token_info['platform'] = 'No data'
    else:
        token_info['hash'] = token_hash[0]
        token_info['hash_url'] = hash_url[0]
        token_info['platform'] = platform[0]
    # print(token_info['hash']) ##
    # print(token_info['hash_url']) ##
    # print(token_info['platform']) ##
    ### Token description ###
    token_description = []
    for desc in coins_hash.find_all('div', class_='sc-1lt0cju-0 srvSa'):
        if desc.div.text != None:
            des = desc.div
            token_description.append(des.text)
    token_info['description'] = token_description[0]
    # print(token_info['description']) ##
    ####################
    ### CMC html scrape token articles ###
    ####################
    url_name = name.replace(' ', '-')
    token_articles = []
    source_articles = requests.get(f'https://coinmarketcap.com/currencies/{url_name}').text
    coins_articles = BeautifulSoup(source_articles, 'lxml')
    block1 = coins_articles.find('div', class_='sc-16r8icm-0 elzRBB container')
    block1_1 = block1.find('div', class_='sc-16r8icm-0 feGaPs desktopShow___2995-')
    article = block1_1.find('div', class_='alexandriaArticles___2__ss')
    links = article.find('ul')
    for li in links.find_all('li'):
        token_articles.append([li.a.text, li.a['href']])
    token_info['info articles'] = token_articles
    # for val in token_info['info articles']:
    #     print(val[0]) ##
    #     print(val[1]) ##
    #     print('-----') ## 
for key, val in token_info.items():
    print(f'{key}: {val}')
print('-----')
#########################
TWITconsumer_key = os.getenv("TWITCONSUMER_KEY")
TWITconsumer_secret = os.getenv("TWITCONSUMER_SECRET")
TWITaccess_token = os.getenv("TWITACCESS_TOKEN")
TWITaccess_token_secret = os.getenv("TWITACCESS_TOKEN_SECRET")

auth = tweepy.OAuthHandler(TWITconsumer_key, TWITconsumer_secret)
auth.set_access_token(TWITaccess_token, TWITaccess_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True,
wait_on_rate_limit_notify=True)

tweets = {} # store all ids and tweets
days = 2 # set the # of 'past' days to pull tweets from, end date
today = datetime.utcnow() # get todays date
end_date = today - timedelta(days=days) # <-- set the end date
end_str = end_date.strftime('%m/%d/%Y') # set the end date as str
start = datetime.now() # set the start date 

### search hashtags ###
print('--- searching hashtags ---')
token_symbol = token_info['symbol']
token_slug = token_info['slug'].replace('-', '')
tags = []
if token_symbol.lower() == token_slug:
    token_tags = [token_symbol, token_symbol+'news', token_symbol+'updates']
    for val in token_tags:
        tags.append(val)
else:
    token_tags = [token_symbol, token_symbol+'news', token_symbol+'updates',
                token_slug, token_slug+'news', token_slug+'updates']
    for val in token_tags:
        tags.append(val)
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

tweets_temp = {}
for key, val in tweets.items():
    if 'rt' not in val[2]:
        val[2] = val[2].split('http', 1)[0]
        if ':' in val[2] == 1:
            val[2] = val[2].split(': ', 1)[1]
            val[2] = re.sub(r'[!@#$]', '', val[2])
            val[2] = "".join(val[2].splitlines())
            tweets_temp[val[1]] = val[0], val[2]
        else:
            val[2] = re.sub(r'[!@#$]', '', val[2])
            val[2] = "".join(val[2].splitlines())
            tweets_temp[val[1]] = val[0], val[2]
temp = []
tweets_res = {}
for key, val in tweets_temp.items():
    if (val[0], val[1][10:20])  not in temp:
        temp.append((val[0], val[1][10:20]))
        tweets_res[key] = val
    else:
        continue

    
print('--- tweets found ---')
print(f'tweets count: {len(tweets)}') # show tweets count

print('--- timer ---')
break1 = datetime.now()
print("Elapsed time: {0}".format(break1-start)) # show timer

print('--- filtered tweets ---')
print(f'tweets count: {len(tweets_res)}') # show tweets count
for key, val in tweets_res.items():
    print(f'{key}: {val}')
    print('-----')
