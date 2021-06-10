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


token_hash = '0x1d2f0da169ceb9fc7b3144628db156f3f6c60dbe'
####################
print('--- scraping holders info ---')
token_holder_info = {}
top_holders = {}
# print(token_info['hash_url'])
# if token_info['hash_url'].index('bscscan') == True:
#     print(token_info['hash_url'])
source_info = requests.get(f'https://bscscan.com/token/{token_hash}').text
source_holders = requests.get(f'https://bscscan.com/token/tokenholderchart/{token_hash}').text
source_description = requests.get(f'https://bscscan.com/token/{token_hash}#tokenInfo').text
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