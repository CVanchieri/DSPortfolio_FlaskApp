import requests
from bs4 import BeautifulSoup
import re 
import os

####################
### pulling token data from CMC api ###
####################
### take user input ###
# user_input = input ("Enter the token name:")
user_input = ['xrp']
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
    token_info['name'] = name
    symbol = value['symbol']
    token_info['symbol'] = symbol
    slug = value['slug']
    token_info['slug'] = slug
    platform = value['platform']
    token_info['platform'] = platform
    date_added = value['date_added']
    token_info['date added'] = date_added
    is_active = value['is_active']
    if is_active != 1:
        token_info['activity'] = 'no'
    else:
        token_info['activity'] = 'yes'
    total_supply = value['total_supply']
    token_info['total supply'] = total_supply
    circulating_supply = value['circulating_supply']
    token_info['circulating supply'] = circulating_supply
    market_cap = value['quote']['USD']['market_cap']        
    token_info['market cap'] = market_cap
    price = value['quote']['USD']['price']
    token_info['price'] = price
    volume_24h = value['quote']['USD']['volume_24h']
    token_info['volume'] = volume_24h
    change_1h = value['quote']['USD']['percent_change_1h']
    token_info['change 1hr'] = change_1h
    change_24h = value['quote']['USD']['percent_change_24h']
    token_info['change 24hr'] = change_24h
    change_7d = value['quote']['USD']['percent_change_7d']
    token_info['change 7d'] = change_7d
    change_30d = value['quote']['USD']['percent_change_30d']
    token_info['change 30d'] = change_30d
    change_60d = value['quote']['USD']['percent_change_60d']
    token_info['change 60d'] = change_60d
    change_90d = value['quote']['USD']['percent_change_90d']
    token_info['change 90d'] = change_90d
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
    token_info['source urls'] = token_urls
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
    token_info['market cap'] = mc1_2text, mc1_change[0]
    ################
    ### Volume stats ###
    b2 = bs_cmc1.find('div', class_='hide___2JmAL statsContainer___2uXZW')
    block2 = b2.select_one('div:nth-child(3)')
    v_text = block2.div.div.text
    v_2text = block2.find('div', class_='statsItemRight___yJ5i-').div.text
    token_info['volume'] = v_2text
    ################
    ### Circulating stats ###
    b3 = b2.select_one('div:nth-child(4)')
    ts_text = b3.select_one('div', class_='sc-16r8icm-0 lpaFj statsLabel___1Mkfd').text
    ts_2text = b3.find('div', class_='sc-16r8icm-0 kkJvVq').div.text
    ts_2perc_text = b3.find('div', class_='supplyBlockPercentage___1g1SF').text
    token_info['circulating supply'] = ts_2text#, ts_2perc_text
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
    token_info['price'] = tr2td_text, tr2td_change[0]
    ### 24hr change stats ###
    tr3 = body.select_one('tr:nth-child(3)')
    tr3_text = tr3.th.text
    tr3td_text = tr3.td.text
    token_info['24hr low / high'] = tr3td_text
    ### Trading volume stats ###
    tr4 = body.select_one('tr:nth-child(4)')
    tr4_text = tr4.th.text
    tr4td_text = tr4.td.text
    tr4td_change = []
    if '-' in tr4td_text:
        tr4td_change.append('-' + tr4.td.div.span.text)
    else: 
        tr4td_change.append('+' + tr4.td.div.span.text)
    token_info['24hr volume'] = tr4td_text, tr4td_change[0]
    ### Market dominance stats ###
    tr5 = body.select_one('tr:nth-child(6)')
    tr5_text = tr5.th.text
    tr5td_text = tr5.td.text
    token_info['market dominance'] = tr5td_text
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
    token_info['hash'] = token_hash[0]
    token_info['hash_url'] = hash_url[0]
    token_info['platform'] = platform[0]
    ### Token description ###
    token_description = []
    for desc in bs_cmc1.find_all('div', class_='sc-1lt0cju-0 srvSa'):
        if desc.div.text != None:
            des = desc.div
            token_description.append(des.text)
    token_info['description'] = token_description[0]
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
    token_info['info articles'] = token_articles

for k, v in token_info.items():
    print(k)