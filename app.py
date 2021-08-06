### necessary imports ### 
from flask import Flask, render_template, request, jsonify, Response
import os
import psycopg2
import pandas as pd
from pandas import DataFrame 
from datetime import datetime, timedelta
from IPython.display import HTML
import requests
import re
from bs4 import BeautifulSoup
import tweepy
import random
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from gensim.parsing.preprocessing import remove_stopwords
from collections import Counter
from functools import wraps

# FalconSQL Login https://api.plot.ly/

"""Create and configure an instance of the Flask application"""
app = Flask(__name__)
### local development ###
# app.config['TESTING'] = True
# app.config['TEMPLATES_AUTO_RELOAD'] = True
# app.config['STATIC_AUTO_RELOAD'] = True
# app.run(debug=True)

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    USERNAME_AUTH = os.getenv("USERNAME_AUTH")
    PASSWORD_AUTH = os.getenv("PASSWORD_AUTH")
    return username == USERNAME_AUTH and password == PASSWORD_AUTH

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


### home page ###
@app.route('/')
def root():
    return render_template('home.html')

### twitterbot ###
@app.route('/twitterbot')
def twitterbot():
    # get AWS information ### 
    AWSdatabase_TWIT = os.getenv("AWSDATABASE_TWIT")
    AWSuser_TWIT = os.getenv("AWSUSER_TWIT")
    AWSpassword_TWIT = os.getenv("AWSPASSWORD_TWIT")
    AWShost_TWIT = os.getenv("AWSHOST_TWIT")
    AWSport_TWIT = os.getenv("AWSPORT_TWIT")
    ## connect to AWS database ###
    connection = psycopg2.connect(database=AWSdatabase_TWIT,
                                user=AWSuser_TWIT,
                                password=AWSpassword_TWIT,
                                host=AWShost_TWIT,
                                port=AWSport_TWIT)
    cur = connection.cursor()
    ### query data & organize data ###
    sql_select_Query = "select * from tweets_storage"
    cur.execute(sql_select_Query)
    data = cur.fetchall()
    df = DataFrame(data)
    df.columns = ['id', 'date', 'name', 'text', 'tags']
    df = df.sort_values('date', ascending=False)
    ### create HTML table ###
    table = HTML(df.to_html(classes='table table-striped'))
    ### close connection ### 
    cur.close()

    return render_template('twitterbot.html',tables=[table])

### covid 19 USA graph ###
@app.route('/covid19usagraph')
def covid19usagraph():
    ### get AWS information ###
    AWSdatabase_COVI = os.getenv("AWSDATABASE_COVI")
    AWSuser_COVI = os.getenv("AWSUSER_COVI")
    AWSpassword_COVI = os.getenv("AWSPASSWORD_COVI")
    AWShost_COVI = os.getenv("AWSHOST_COVI")
    AWSport_COVI = os.getenv("AWSPORT_COVI")
    ### connect to AWS database ###
    connection = psycopg2.connect(database=AWSdatabase_COVI,
                                user=AWSuser_COVI,
                                password=AWSpassword_COVI,
                                host=AWShost_COVI,
                                port=AWSport_COVI)
    cur = connection.cursor()                           
    print("connected to database")
    ### query data ###
    sql_select_Query = "select * from covid19us"
    cur.execute(sql_select_Query)
    data = cur.fetchall()
    df = DataFrame(data)
    ### clean and organize data ###
    df.columns = ['Date', 'States', 'TestsToday', 'TestsDailyChange', 'TotalTests', 'PositivesToday', 'PostiviesDailyChange', 'TotalPositives', 
            'NegativesToday', 'NegativesDailyChange', 'TotalNegatives',
            'HospitalizedToday', 'HospitalizedDailyChange', 'HospitalizedCurrently', 'TotalHospitalized', 
            'IcuToday', 'IcuDailyChange', 'IcuCurrently', 'TotalIcu', 
            'VentilatorsToday', 'VentilatorsDailyChange', 'VentilatorsCurrently', 'TotalVentilators', 
            'DeathsToday', 'DeathsDailyChange', 'TotalDeaths', 'RecoveredToday', 'RecoveredDailyChange', 'TotalRecovered'] 
    df = df.sort_values('Date', ascending=False)     
    df.reset_index(drop=True)       
    pos = lambda x: "+"+str(x) if x>0 else x
    ### add + to positive values ### 
    df['TestsDailyChange'] = df['TestsDailyChange'].apply(pos)
    df['PostiviesDailyChange'] = df['PostiviesDailyChange'].apply(pos)
    df['NegativesDailyChange'] = df['NegativesDailyChange'].apply(pos)
    df['HospitalizedDailyChange'] = df['HospitalizedDailyChange'].apply(pos)
    df['IcuDailyChange'] = df['IcuDailyChange'].apply(pos)
    df['VentilatorsDailyChange'] = df['VentilatorsDailyChange'].apply(pos)
    df['DeathsDailyChange'] = df['DeathsDailyChange'].apply(pos)
    df['RecoveredDailyChange'] = df['RecoveredDailyChange'].apply(pos)
    print("cleaned data")
    ### set today's numbers ###
    today_date = df.Date[0]
    today_hospitalized = int(df.HospitalizedToday[0])
    today_icu = int(df.IcuToday[0])
    today_ventilators = int(df.VentilatorsToday[0])
    today_deaths =int(df.DeathsToday[0])
    today = [today_date, "{:,}".format(today_hospitalized), "{:,}".format(today_icu),
                "{:,}".format(today_ventilators), "{:,}".format(today_deaths)]       
    today_change = [df.HospitalizedDailyChange[0], df.IcuDailyChange[0],
                    df.VentilatorsDailyChange[0], df.DeathsDailyChange[0]]     
    ### close connection ###       
    cur.close()

    return render_template('covid19usagraph.html', today = today, change = today_change)#, yesterday = yesterday)

### covid 19 USA data ###
@app.route('/covid19usadata')
def covid19usadata():
    ### get AWS information ###
    AWSdatabase_COVI = os.getenv("AWSDATABASE_COVI")
    AWSuser_COVI = os.getenv("AWSUSER_COVI")
    AWSpassword_COVI = os.getenv("AWSPASSWORD_COVI")
    AWShost_COVI = os.getenv("AWSHOST_COVI")
    AWSport_COVI = os.getenv("AWSPORT_COVI")
    ## connect to AWS database ###
    connection = psycopg2.connect(database=AWSdatabase_COVI,
                                user=AWSuser_COVI,
                                password=AWSpassword_COVI,
                                host=AWShost_COVI,
                                port=AWSport_COVI)
    cur = connection.cursor()
    ### query and organize data ###
    sql_select_Query = "select * from covid19us"  
    cur.execute(sql_select_Query)
    data = cur.fetchall()
    df = DataFrame(data)  
    df.columns = ['Date', 'States', 'TestsToday', 'TestsDailyChange', 'TotalTests', 'PositivesToday', 'PostiviesDailyChange', 'TotalPositives', 
            'NegativesToday', 'NegativesDailyChange', 'TotalNegatives',
            'HospitalizedToday', 'HospitalizedDailyChange', 'HospitalizedCurrently', 'TotalHospitalized', 
            'IcuToday', 'IcuDailyChange', 'IcuCurrently', 'TotalIcu', 
            'VentilatorsToday', 'VentilatorsDailyChange', 'VentilatorsCurrently', 'TotalVentilators', 
            'DeathsToday', 'DeathsDailyChange', 'TotalDeaths', 'RecoveredToday', 'RecoveredDailyChange', 'TotalRecovered']
    ### create HTML table ###
    table = HTML(df.to_html(classes='table table-striped'))
    ### close connection ###
    cur.close()

    return render_template('covid19usadata.html',tables=[table])

### coinscraper ###
@app.route('/coinscraper')
def coin_scrape():
    ####################
    ### scraping new tokens from CMC html ### 
    ####################
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
    return render_template('coinscraper.html', new_token_data=new_tokens)
####################
@app.route('/coinscraper', methods = ['POST'])
def coin_scrape_result():
    ####################
    ### scraping new tokens from CMC html ### 
    ####################
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
    ####################
    ### pulling token data from CMC api ###
    ####################
    ### take user input ###
    # user_input = input ("Enter the token name:")
    user_input = request.form['user_input']
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
        coin_scrape_stats = coin_stats2.find('div', class_='sc-16r8icm-0 jIZLYs container___E9axz')
        if coin_scrape_stats != None:
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
        if coins_hash.find_all('div', class_='sc-1lt0cju-0 srvSa') != None:
            for desc in coins_hash.find_all('div', class_='sc-1lt0cju-0 srvSa'):
                # if desc.div.text != 0:
                    des = desc.div
                    if des != None:
                        token_description.append(des.text)
            if len(token_description) > 0:
                token_info['description'] = token_description[0]
        # print(token_info['description']) ##
##########################
    print('--- scraping holders info ---')
    token_holder_info = {}
    top_holders = {}
    if 'bsc' in token_info['hash_url']:
        source_info = requests.get(f'https://bscscan.com/token/{token_info["hash"]}').text
        source_holders = requests.get(f'https://bscscan.com/token/tokenholderchart/{token_info["hash"]}').text
        source_description = requests.get(f'https://bscscan.com/token/{token_info["hash"]}#tokenInfo').text
        soup_1 = BeautifulSoup(source_info, 'lxml')
        soup_2 = BeautifulSoup(source_holders, 'lxml')
        soup_3 = BeautifulSoup(source_description, 'lxml')
        overview = soup_1.find('div', class_='row mb-4')
        ####################
        card_4 = soup_3.find('div', id='ContentPlaceHolder1_maintab')
        token = overview.find('div', class_='font-weight-medium').b.text
        description = card_4.find('div', id='tokenInfo').div.text
        description = description.split('MarketVolume', 1)
        description = description[0]
        description = description[9:]
        supply = overview.find('span', class_='hash-tag text-truncate').text
        c_supply = overview.find('span', class_='text-secondary ml-1').text
        num_holders = overview.find('div', class_='mr-3').text
        num_holders = num_holders[1:-3]
        ####################
        url = []
        for card in soup_1.find_all('div', class_='col-md-6'):
            if card.find('h2', class_='card-header-title') != None and card.find('div', class_='col-md-4').text == 'Contract:':
                contract = card.find('a', class_='text-truncate d-block mr-2').text
                url_t = card.find('div', id='ContentPlaceHolder1_tr_officialsite_1')
                url_t = url_t.find('div', class_='col-md-8').a['href']
                url.append(url_t)
        ####################
        card_2 = soup_2.find('div', id='ContentPlaceHolder1_resultrows')
        ta = soup_2.find('div', class_='mb-0').p.text[1:-1]
        ta = ta.replace('token', 'tokens')
        desc_1 = ta.replace('tokenss', 'tokens')
        card_3 = soup_2.find('div', class_='card-header py-4')
        # desc_2 = blockchair_url.split('.com/', 1)
        # token_name = name[1].upper()
        token_holder_info[token] = [num_holders, url[0], description, desc_1]
        #########################
        for addre in card_2.find_all('tr')[:6]:
            rank = []
            holder = []
            hash = []
            holder_hash = []
            holder_hash_url = []
            exchange = []
            quantity = []
            percentage = []

            if addre.select_one('td:nth-child(1)') != None:
                rank.append(addre.select_one('td:nth-child(1)').contents[0])

                holder_name = addre.select_one('td:nth-child(2)').span
                hash_t = holder_name.a['href']
                hash.append(re.sub(r'^.*?=', '=', hash_t))

                holder_hash_t = hash[0][1:]
                holder_hash.append(holder_hash_t)
                holder_hash_url.append('https://bscscan.com/address/' + holder_hash[0])

                if ': ' in holder_name.a.text:
                    exch, nam = holder_name.a.text.split(':')
                    exchange.append(exch)
                    holder.append(nam)

                    quant = addre.select_one('td:nth-child(3)').contents[0]
                    quantity.append(quant)

                    perc = addre.select_one('td:nth-child(4)').contents[0]
                    percentage.append(perc)

                    top_holders[rank[0]] = [holder[0], holder_hash[0], holder_hash_url[0], quantity[0], percentage[0], exchange[0]]
                else:
                    no_exchange = 'Exchange: Missing'
                    exchange.append(no_exchange)

                    nam = holder_name.a.text
                    holder.append(nam)

                    quant = addre.select_one('td:nth-child(3)').contents[0]
                    quantity.append(quant)

                    perc = addre.select_one('td:nth-child(4)').contents[0]
                    percentage.append(perc)

                    top_holders[rank[0]] = [holder[0], holder_hash[0], holder_hash_url[0], quantity[0], percentage[0], exchange[0]]

    for k, v in token_holder_info.items():
        print(f'{k}: {v}')
        print('-----')
    print('-----')
    for k, v in top_holders.items():
        print(f'{k}: {v}')
        print('-----')
##########################
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


    ######################
    REDclient_id = os.getenv("RED_CLIENT_ID")
    REDsecret_key = os.getenv("RED_SECRET_KEY")
    REDusername = os.getenv("RED_USERNAME")
    REDpassword = os.getenv("RED_PASSWORD")
    auth = requests.auth.HTTPBasicAuth(REDclient_id, REDsecret_key)
    data = {
            'grant_type': 'password',
            'username': REDusername,
            'password': REDpassword,
            }
    headers = {'User-Agent': 'MyAPI/0.0.1'}
    print('--- searching reddit posts ---')
    res = requests.post('https://www.reddit.com/api/v1/access_token', 
                        auth=auth, data=data, headers=headers)
    TOKEN = res.json()['access_token']
    headers = {**headers, **{'Authorization': f'bearer {TOKEN}'}}
    # print(headers)
    # print(requests.get('https://oauth.reddit.com/api/v1/me', headers=headers).json())
    sub_posts = {}
    sub_res2 = requests.get('https://oauth.reddit.com/r/' + token_slug + '/new', 
                    headers=headers)
    if sub_res2.json() != None:
        for post in sub_res2.json()['data']['children'][:10]:
            # print(sub_res2.json())
            # subreddit = post['data']['subreddit']
            # if symbol in post['data']['title'] != None:
            title = post['data']['title']
            for k, v in post.items():
                if 'selftext' in v:
                    text = post['data']['selftext']
                    text = "".join(text.splitlines())
                    text = re.sub(r'[&@#]', '', text)
                    score = post['data']['score']
                    # posts.append([text, ups, downs, score])
                    sub_posts[title] = [text, score]
            # print(f'title: {title}')
            # print(f'text: {text}')
            # print(f'score: {score}')
            # print('-----')
            # print(post)

    print('--- posts found ---')
    print(f'posts count: {len(sub_posts)}') # show tweets count
    for k, v in sub_posts.items():
        print(f'{k}: {v}')
        print('-----')

    return render_template('coinscraper.html', token_data=token_info.items(), token_holder=token_holder_info.items(), top_holders=top_holders.items(), tweets_data=tweets_res.items(), reddit_data=sub_posts.items(), new_token_data=new_tokens)

    ####################
    ### text image creator ###
@app.route('/textimage')
def text_image():
    
    return render_template('textimageentry.html')

@app.route('/textimage', methods = ['POST'])
@requires_auth
def text_image2():
    # user_input = "jay z"
    user_input = request.form['user_input']
    user_input = user_input.replace(' ', '-')
    user_input = user_input.replace(' ', '')

    ### start timer ###
    start = datetime.now()

    ### scraping song links ###
    print('--- scraping song links ---')
    source = requests.get(f'https://www.songlyrics.com/{user_input}-lyrics/').text
    soup = BeautifulSoup(source, 'lxml')
    songlist = soup.find('div', class_='listbox')
    tracklist = songlist.find('table', class_='tracklist').tbody
    song_links = []
    artist_details = []
    for song in tracklist.find_all('tr', itemprop="itemListElement"):
        if song.td.text in [str(x) for x in range(200 + 1)]:
            link = song.find('a')['href']
            if link not in song_links:
                song_links.append(link)

    ### collecting song details ###
    print('--- scraping song details text ---')
    for val in song_links:
        song_title = val[27:-1].split('/', 1)[1]
        song_title = song_title[:-6].replace('-', ' ').capitalize()
        artist_name = user_input.replace('-', ' ').capitalize()

    ### scraping song text ###
        songsource = requests.get(val).text
        soup2 = BeautifulSoup(songsource, 'lxml')
        block = soup2.find('div', id='songLyricsContainer')
        if block.find('p').text != False:
            text = block.find('p').text
            permitted = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "
            songtext = text.lower()
            songtext = ' '.join(word for word in songtext.split() if word[0]!='[')
            songtext = songtext.replace("\n", " ").strip()
            songtext = "".join(c for c in songtext if c in permitted)
            songtext = songtext.replace("    ", " ")
            songtext = songtext.replace("   ", " ")
            songtext = songtext.replace("  ", " ")
            artist_details.append(songtext)

    print('--- combining song text ---')
    textblock = ' '.join([str(w) for w in random.sample(artist_details, len(artist_details))])
    textblock = textblock * 2
    print('--- length of text ---')
    print(len(textblock))
    # textblock = '. '.join(artist_details)
    print(f'songs = {len(artist_details)}')
    print(len(textblock))
    print(textblock)

    #### finish timer ###
    print('--- runtime ---')
    break1 = datetime.now()
    print("Elapsed time: {0}".format(break1-start)) # show timer
    
    # text = ''' 
    # you want more want more you think its the end but its just the beginning you think its the end but its just the beginning go down backbiter down backbite down backbiter down backbite down backbiter down backbiter down backbiter down backbite they stab you in the back and they claim that youre not looking but jah have them in the region in the valley of decision they stab you in the back and they claim that youre not looking but jah have em in the region in the valley of decision in the valley of decision go down backbiter down backbite down backbiter down backbite now you get what you want do you want more now you get what you want do you want more now you get what you want do you want more you think its the end ado you do you want more go down backbiter down backbite down backbiter down backbite down backbiter down backbite down backbiter down backbite they stab you in the back stab you in the back and they claim that youre not looking claim that youre not looking but jah have them in the region jah have them in the region in the valley of decision now what you want want more want more now what you get want more want more now now do you want more you think its the end you think its the end do you want more want more you think its the end now what you want want more want more now what you get want more want more hey happy people this here is something new i know youre gonna like it so let me tell you what were gonna do souls almighty dont you know we got the rhythm souls almighty we are willing funky funky chicken and the mashed potato do the alligator lets do it together souls almighty do you dig me yall souls almighty my soul is raw get yourself together in any kind of weather things will be mighty better if you get it together souls almighty dont you know we got the rhythm souls almighty get yourself yourself together in any kind of weather things will be mighty better if we if we get it together souls dont you know we got the rhythm hit it brother souls almighty o baby when youre not with him funky funky chicken and the mashed potato do the alligator do it together yall shocks of souls and shocks souls and shocks we got we got we got the rhythm sing your song brother my babys with him ooh get yourself together in any kind of weather things will be mighty better do it twice you know that i love you baby but you just wont let me you know that i love you baby but you just wont let me every morning i get up i sip my cup my eyes get red noone to hear me one more thing id like to say right here baby but you just wont let me one more thing id like to say right here baby but y
    # '''
    # permitted = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "
    # text = text.replace("\n", " ").strip()
    # text = "".join(c for c in text if c in permitted)
    # text = text.replace("    ", " ")
    # text = text.replace("   ", " ")
    # text = text.replace("  ", " ")
    # text = text.lower()
    # textblock = text * 1000
    return render_template('textimagedone.html', text=textblock)

@app.route('/artistanalyzer')
def artistanalyzer():

    return render_template('artistanalyzer.html')


@app.route('/artistanalyzer', methods = ['POST'])
def artistanalyzer_result():
    # user_input = "jay z"
    user_input = request.form['user_input']
    user_input = user_input.replace(' ', '-')
    user_input = user_input.replace(' ', '')

    ### start timer ###
    start = datetime.now()

    ### scraping song links ###
    print('--- scraping song links ---')
    source = requests.get(f'https://www.songlyrics.com/{user_input}-lyrics/').text
    soup = BeautifulSoup(source, 'lxml')
    songlist = soup.find('div', class_='listbox')
    tracklist = songlist.find('table', class_='tracklist').tbody
    song_links = []
    artist_details = []
    for song in tracklist.find_all('tr', itemprop="itemListElement"):
        if song.td.text in [str(x) for x in range(50 + 1)]:
            link = song.find('a')['href']
            if link not in song_links:
                song_links.append(link)
    ### collecting song details ###
    print('--- scraping song details text ---')
    for val in song_links:
        song_title = val[27:-1].split('/', 1)[1]
        song_title = song_title[:-6].replace('-', ' ').capitalize()
        artist_name = user_input.replace('-', ' ').title()
    ### scraping song text ###
        songsource = requests.get(val).text
        soup2 = BeautifulSoup(songsource, 'lxml')
        block = soup2.find('div', id='songLyricsContainer')
        if block.find('p').text != False:
            text = block.find('p').text
            if 'feat.' not in text:
                permitted = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "
                songtext = text.lower()
                songtext = ' '.join(word for word in songtext.split() if word[0]!='[')
                songtext = songtext.replace("\n", " ").strip()
                songtext = "".join(c for c in songtext if c in permitted)
                songtext = songtext.replace("  ", " ").capitalize()
                artist_details.append([artist_name, song_title, songtext])
    ### create a data frame ###
    print('--- Data Frame ---')
    df = pd.DataFrame (artist_details,columns=['Artist Name', 'Song Title', 'Song Text'])                    
    ### analysing text ###
    # def sent_to_words(sentence):
    #         yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))
    top_words = []
    num_words = []
    pol_sent = []
    analyzer= SentimentIntensityAnalyzer()
    for val in df['Song Text']:
        res = len(val.split())
        num_words.append(res)
        val = remove_stopwords(val.lower())

        polar = analyzer.polarity_scores(val)
        es = list(polar.items())
        pol = list(es[-1])
        song_1 = ' '.join(word for word in val.split() if len(word)>3)
        split_val = song_1.split()
        count = Counter(split_val)
        comm = count.most_common(5)
        top_words.append(comm)
        pol_sent.append(pol[1])
    df['Num Words'] = num_words
    df['Top Words'] = top_words
    df['Pol Scores'] = pol_sent

    length_song = df['Num Words'].max()
    long_song = list(df.loc[df['Num Words'] == length_song, 'Song Title'])
    df = df[['Artist Name', 'Song Title', 'Song Text', 'Num Words', 'Top Words', 'Pol Scores']]
    list_2 = list(df['Pol Scores'])
    pol_list = []
    for val in list_2:
        if val > .50:
            val_ = ['Positive']
            pol_list.append(val_)
        elif val < .50:
            val_ = ['Negative']
            pol_list.append(val_)
        elif val == .50:
            val_ = ['Neutral']
            pol_list.append(val_)
    df['+/-'] = pol_list
    df = df[df['Song Text'] != 'We do not have the lyrics for soon come yet']
    table = HTML(df.to_html(classes='table table-striped'))
    pos_out = df['+/-'].mode()
    total_pol = pos_out[0][0]
    artist_name = df["Artist Name"][0]
    num_songs = len(df)
    num_words = df["Num Words"].sum()
    longest_song = long_song[0]
    longestword_count = df['Num Words'].max()
    dict_data = {'Artist Name':artist_name, 
                'Number of Songs':num_songs, 
                'Number of Words':num_words, 
                'Longest Song':longest_song, 
                'Longest Song Word Count':longestword_count, 
                "Artist's Overall Polarity":total_pol}
    ### data frame ###
    # print(df.shape)
    # print(df.head())
    print(f'Artist Name: {artist_name}')
    print(f'Total number of songs: {num_songs}')
    print(f'Total Number of Words: {num_words}')
    print(f'Song with most words: {longest_song}, word count: {longestword_count}')
    print(f'Overall polarity: {total_pol}')
    print('-----')
    #### finish timer ###
    print('--- runtime ---')
    break1 = datetime.now()
    print("Elapsed time: {0}".format(break1-start)) # show timer
    
    return render_template('artistanalyzer.html', tables=[table], data=dict_data.items())
