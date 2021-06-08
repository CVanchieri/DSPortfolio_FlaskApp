import requests
CLIENT_ID = 'T9wY5Ulq8tLW6w'
SECRET_KEY ='L7eznyEuLAotFRL_HADO0m9t6mg6WA'

auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_KEY)
data = {
        'grant_type': 'password',
        'username': 'GnarlyCharley6',
        'password': 'Charryn84',
        }

headers = {'User-Agent': 'MyAPI/0.0.1'}
res = requests.post('https://www.reddit.com/api/v1/access_token', 
                    auth=auth, data=data, headers=headers)

TOKEN = res.json()['access_token']
headers = {**headers, **{'Authorization': f'bearer {TOKEN}'}}
# print(headers)

# print(requests.get('https://oauth.reddit.com/api/v1/me', headers=headers).json())
symbol = 'shib'
payload = {'q' :symbol, 'limit':5, 'sort': 'relevance'}
res = requests.get('https://oauth.reddit.com' + '/subreddits/search', 
                    params=payload,
                    headers=headers)
# print(res.json())
for post in res.json()['data']['children']:
    description = post['data']['description']
    # subreddit = post['data']['subreddit']
    # if symbol in post['data']['title'] != None:
    title = post['data']['title']
#     text = post['data']['selftext']
#     ups = post['data']['ups']
#     downs = post['data']['downs']
#     score = post['data']['score']


#     # print(subreddit)
    print(title)
    print(description)

#     print(text)
#     print(ups)
#     print(downs)
#     print(score)
    print('-----')

print(res.json())