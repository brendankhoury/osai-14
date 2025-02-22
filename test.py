import requests

with open('article.txt', 'r') as file:
    article_content = file.read().replace('"', '\\"')

data = {
    "article": article_content
}

response = requests.post(
    'http://127.0.0.1:5000/check_article',
    json=data,
    headers={'Content-Type': 'application/json'}
)

print(response.text)
