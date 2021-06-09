import requests
import regex as re
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
slug = 'cardano'
# payload = {'q' :symbol, 'limit':5, 'sort': 'relevance'}
# sub_res = requests.get('https://oauth.reddit.com' + '/subreddits/search', 
#                     params=payload,
#                     headers=headers)
# # print(sub_res.json())
# sub_reddits = []
# for sub in sub_res.json()['data']['children'][:1]:
#     description = sub['data']['description']
#     # subreddit = post['data']['subreddit']
#     # if symbol in post['data']['title'] != None:
#     title = sub['data']['title']
#     sub_reddits.append(title)
#     # print(sub)
# #     text = post['data']['selftext']
# #     ups = post['data']['ups']
# #     downs = post['data']['downs']
# #     score = post['data']['score']

# #     # print(subreddit)
# print(sub_reddits)
#     # print(description)
sub_posts = {}

sub_res2 = requests.get('https://oauth.reddit.com/r/' + slug + '/new', 
                headers=headers)
for post in sub_res2.json()['data']['children'][:10]:
    # print(sub_res2.json())
    # subreddit = post['data']['subreddit']
    # if symbol in post['data']['title'] != None:
    title = post['data']['title']
    text = post['data']['selftext']
    text = "".join(text.splitlines())
    text = re.sub(r'[&@#]', '', text)
    score = post['data']['score']
    # posts.append([text, ups, downs, score])
    sub_posts[title] = [text, score]
    print(f'title: {title}')
    print(f'text: {text}')
    print(f'score: {score}')
    print('-----')
    # print(post)
# for k, v in sub_posts.items():
#     print(f'{k}: {v}')
#     print('-----')