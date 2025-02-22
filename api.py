from flask import Flask, request, jsonify
import requests
from observer import PRMonitorAgent
import json
from twilio.rest import Client
app = Flask(__name__)

monitorAgent = PRMonitorAgent()

def send_alert(message):
    webhook_url = "https://discord.com/api/webhooks/1342998251770740776/CWhA8IXewHg4zB3-_uNM56UZJ5OrL-IkD9ad2oCsg9r5cwg1OGUu6zq06eelP1a6Sgx6"
    payload = {
        "content": message
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
    if response.status_code != 204:
        print(f"Failed to send alert: {response.status_code}, {response.text}")

@app.route('/check_article', methods=['POST'])
def check_article():
    print(f"DATA {request}")
    try:
        data = request.get_json()
    except:
        return jsonify({'error': 'Invalid JSON'}), 400
    if not data or 'article' not in data:
        return jsonify({'error': 'No article provided'}), 400
    
    article = data['article']
    # Here you can add your logic to process the article
    # For example, you can check the length of the article

    result = monitorAgent.check_article(article)
    print(result)
    return result, 200
@app.route('/check_article_url', methods=['POST'])
def check_article_url():
    try:
        data = request.get_json()
    except:
        return jsonify({'error': 'Invalid JSON'}), 400
    if not data or 'url' not in data:
        return jsonify({'error': 'No URL provided'}), 400
    
    url = data['url']
    # Here you can add your logic to process the URL

    result = monitorAgent.check_article_url(url)
    print(type(result))
    print(result)
    # result = "{\"monitors\": " + result[1:-1] + "}"
    # result = json.loads(result)
    # Parse the result string into a JSON object
    result = json.loads(result)
    print(type(result))
    result = json.loads(result)
    print(type(result))
    print("Result: " + str(result))
    for i in result: 
        print(i)
        if i['risk'] == 'critical':
            message = (
                f"Critical risk detected in article:\n"
                f"Monitor Triggered: {i['monitor']}\n"
                f"Reason: {i['reason']}\n"
                f"Risk Assessment: {i['risk']}"
            )
            send_alert(message)
    return result, 200

if __name__ == '__main__':
    app.run(debug=True)
