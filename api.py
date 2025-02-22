from flask import Flask, request, jsonify
from observer import PRMonitorAgent
import json
app = Flask(__name__)

monitorAgent = PRMonitorAgent()

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


if __name__ == '__main__':
    app.run(debug=True)