import requests
response = requests.post(
    'http://127.0.0.1:5000/check_article_url',
    json={"url": "https://iharare.com/samsung-phone-batteries-are-exploding-again-here-are-the-models-to-avoid/"},
    headers={'Content-Type': 'application/json'}
)

print(response.text)
