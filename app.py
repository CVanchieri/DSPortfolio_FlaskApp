### necessary imports ### 
from flask import Flask, render_template, request
import os
import psycopg2
import pandas
from pandas import DataFrame 
from IPython.display import HTML
import requests
import re
from bs4 import BeautifulSoup


# FalconSQL Login https://api.plot.ly/

"""Create and configure an instance of the Flask application"""
app = Flask(__name__)
### local development ###
# app.config['TESTING'] = True
# app.config['TEMPLATES_AUTO_RELOAD'] = True
# app.config['STATIC_AUTO_RELOAD'] = True
# app.run(debug=True)


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
    
    return render_template('coinscraper.html')

@app.route('/coinscraper', methods = ['POST'])
def coin_scrape_result():
    ####################
    ### pulling token data from CMC api ###
    ####################
    ### take user input ###
    # user_input = input ("Enter the token name:")
    user_input = request.form['user_input']
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
    query_data = requests.get(x_query, params=params , headers=headers).json()
    coins_query = query_data['data']
    token_info = {}
    for key, value in coins_query.items():
        name = value['name']
        token_info['token name'] = name
        symbol = value['symbol']
        token_info['token symbol'] = symbol
        slug = value['slug']
        token_info['token slug'] = slug
        platform = value['platform']
        token_info['token platform'] = platform
        date_added = value['date_added']
        token_info['token date_added'] = date_added
        is_active = value['is_active']
        if is_active != 1:
            token_info['token activity'] = 'no'
        else:
            token_info['token activity'] = 'yes'
        total_supply = value['total_supply']
        token_info['token total_supply'] = total_supply
        circulating_supply = value['circulating_supply']
        token_info['token circulating supply'] = circulating_supply
        market_cap = value['quote']['USD']['market_cap']        
        token_info['token market cap'] = market_cap
        price = value['quote']['USD']['price']
        token_info['token price'] = price
        volume_24h = value['quote']['USD']['volume_24h']
        token_info['token volume'] = volume_24h
        change_1h = value['quote']['USD']['percent_change_1h']
        token_info['token change 1hr'] = change_1h
        change_24h = value['quote']['USD']['percent_change_24h']
        token_info['token change 24hr'] = change_24h
        change_7d = value['quote']['USD']['percent_change_7d']
        token_info['token change 7d'] = change_7d
        change_30d = value['quote']['USD']['percent_change_30d']
        token_info['token change 30d'] = change_30d
        change_60d = value['quote']['USD']['percent_change_60d']
        token_info['token change 60d'] = change_60d
        change_90d = value['quote']['USD']['percent_change_90d']
        token_info['token change 90d'] = change_90d
        ####################
        ### CMC api token urls ###
        ####################
        meta_data = requests.get(x_meta, params=params , headers=headers).json()
        coins_meta = meta_data['data']
        token_urls = []
        for key, value2 in coins_meta.items():
            if value['name'] == value2['name']:
                logo = value2['logo']
                for x in value2['urls']['explorer']:
                    token_urls.append(x)
        token_info['token urls'] = token_urls
        ####################
        ### CMC html scrape token stats1 ###
        ####################
        url_name = name.replace(' ', '-')
        source_1 = requests.get(f'https://coinmarketcap.com/currencies/{url_name}').text
        bs_cmc1 = BeautifulSoup(source_1, 'lxml')
        block1 = bs_cmc1.find('div', class_='statsBlock___11SXA').div
        mc1_text = block1.div.text
        mc1_2text = block1.select_one('div:nth-child(2)').div.text
        mc1_change = []
        if '-' in mc1_2text:
            mc1_change.append('-' + block1.select_one('div:nth-child(2)').span.text)
        else: 
            mc1_change.append('+' + block1.select_one('div:nth-child(2)').span.text)
        token_info['token market cap'] = mc1_2text, mc1_change[0]
        ################
        ### Volume stats ###
        b2 = bs_cmc1.find('div', class_='hide___2JmAL statsContainer___2uXZW')
        block2 = b2.select_one('div:nth-child(3)')
        v_text = block2.div.div.text
        v_2text = block2.find('div', class_='statsItemRight___yJ5i-').div.text
        token_info['token volume'] = v_2text
        ################
        ### Circulating stats ###
        b3 = b2.select_one('div:nth-child(4)')
        ts_text = b3.select_one('div', class_='sc-16r8icm-0 lpaFj statsLabel___1Mkfd').text
        ts_2text = b3.find('div', class_='sc-16r8icm-0 kkJvVq').div.text
        ts_2perc_text = b3.find('div', class_='supplyBlockPercentage___1g1SF').text
        token_info['token circulating supply'] = ts_2text#, ts_2perc_text
        ####################
        ### CMC html scrape token stats2 ###
        ####################
        stats = bs_cmc1.find('div', class_='sc-16r8icm-0 jIZLYs container___E9axz')
        body = stats.find('tbody')
        ### Price stats ###
        tr2 = body.select_one('tr:nth-child(2)')
        tr2_text = tr2.th.text
        tr2td_text = tr2.td.span.text
        tr2td_change = []
        if '-' in tr2td_text:
            tr2td_change.append('-' + tr2.td.div.span.text)
        else: 
            tr2td_change.append('+' + tr2.td.div.span.text)
        token_info['token price'] = tr2td_text, tr2td_change[0]
        ### 24hr change stats ###
        tr3 = body.select_one('tr:nth-child(3)')
        tr3_text = tr3.th.text
        tr3td_text = tr3.td.text
        token_info['token 24hr low / high'] = tr3td_text
        ### Trading volume stats ###
        tr4 = body.select_one('tr:nth-child(4)')
        tr4_text = tr4.th.text
        tr4td_text = tr4.td.text
        tr4td_change = []
        if '-' in tr4td_text:
            tr4td_change.append('-' + tr4.td.div.span.text)
        else: 
            tr4td_change.append('+' + tr4.td.div.span.text)
        token_info['token 24hr volume'] = tr4td_text, tr4td_change[0]
        ### Market dominance stats ###
        tr5 = body.select_one('tr:nth-child(6)')
        tr5_text = tr5.th.text
        tr5td_text = tr5.td.text
        token_info['token market dominance'] = tr5td_text
        ####################
        ### CMC html scrape token hash ###
        ####################
        url_name = name.replace(' ', '-')
        token_hash = []
        hash_url = []
        platform = []
        source_1 = requests.get(f'https://coinmarketcap.com/currencies/{url_name}').text
        bs_cmc1 = BeautifulSoup(source_1, 'lxml')
        ### Token hash ###
        for head in bs_cmc1.find_all('div', class_='sc-16r8icm-0 dOJIkS container___2dCiP contractsRow'):

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
        token_info['token hash'] = token_hash[0]
        token_info['token hash_url'] = hash_url[0]
        token_info['token platform'] = platform[0]
        ### Token description ###
        token_description = []
        for desc in bs_cmc1.find_all('div', class_='sc-1lt0cju-0 srvSa'):
            if desc.div.text != None:
                des = desc.div
                token_description.append(des.text)
        token_info['token description'] = token_description[0]
        ####################
        ### CMC html scrape token articles ###
        ####################
        url_name = name.replace(' ', '-')
        token_articles = []
        source_2 = requests.get(f'https://coinmarketcap.com/currencies/{url_name}').text
        bs_cmc2 = BeautifulSoup(source_2, 'lxml')
        sp = bs_cmc2.find('div', class_='sc-16r8icm-0 elzRBB container')
        hold = sp.find('div', class_='sc-16r8icm-0 feGaPs desktopShow___2995-')
        article = hold.find('div', class_='alexandriaArticles___2__ss')
        links = article.find('ul')
        for li in links.find_all('li'):
            token_articles.append([li.a.text, li.a['href']])
        token_info['token articles'] = token_articles

    return render_template('coinscraper.html', data=token_info.items())