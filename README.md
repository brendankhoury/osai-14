# AI Risk Monitoring Agent

## Overview

The **AI Risk Monitoring Agent** is a real-time solution that scans articles and assesses their potential risk to a company. By evaluating articles based on predefined risk factors related to company interests, it can determine whether an article is **high risk**, **medium risk**, or **low risk**. The agent sends notifications via **Discord webhooks** to a user, alerting them of high-risk articles and providing critical information for swift decision-making.

## Features

- **Real-Time Article Monitoring**: The agent continuously scans articles from various sources and provides instant risk assessments.
  
- **AI-Powered Risk Classification**: Using AI, the agent classifies articles into **high**, **medium**, or **low** risk categories based on predefined criteria, including:
  - Potential negative impact on company reputation
  - Public/customer sentiment or media attention
  - Likelihood of escalation
  - Urgency of the situation
  
- **Critical Alerts via Discord**: When a **high-risk article** is identified, the agent sends a detailed notification via Discord, summarizing the article and providing reasoning for its classification.
  
- **Customizable Risk Criteria**: Adjust the criteria that define what constitutes high, medium, or low risk to match your specific business needs.


## Tech Stack 

- Python, Flask, Requests
- OpenAI GPT-4 for classification
- LlamaIndex for vector embeddings
- Newspaper3k for article parsing
- Discord Webhooks for alerts

## How it works
```pgsql

         +----------------+
         | New Article     |
         | (URL or Text)  |
         +--------+-------+
                  |
                  v
       +----------------------+
       | Article Parsing      |
       | (Newspaper3k)        |
       +----------------------+
                  |
                  v
       +----------------------+
       | AI Risk Classification|
       | (GPT-4 via LlamaIndex)|
       +----------------------+
                  |
        +---------+---------+
        |                   |
        v                   v
+----------------+   +------------------+
| Low/Medium Risk|   | High-Risk Alert  |
| Store or Log   |   | Discord Notification|
+----------------+   +------------------+
```

## Usage 
 - Monitor Articles by URL
``` bash
POST /check_article_url
{
  "url": "https://www.example.com/news-article"
}
```
 - Monitor Raw Text
```bash
   POST /check_article
{
  "article": "Article text here..."
}
```
High-risk articles trigger Discord alerts with a summary and reason.

## Example Output 
```
{
  "classification": "High-Risk",
  "summary": "The article discusses Samsung phone battery explosions and the company's inadequate response.",
  "reason": "Potential damage to reputation and negative public opinion."
}
```

## Installation
   ```bash
   git clone https://github.com/your-repo-name.git

   git clone https://github.com/your-username/ai-risk-monitoring-agent.git

   cd ai-risk-monitoring-agent
  
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
    
   pip install -r requirements.txt
    
   # Add your API keys in a .env file
   OPENAI_API_KEY=your_openai_api_key
   DISCORD_WEBHOOK_URL=your_discord_webhook

  ```

