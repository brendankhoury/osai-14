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

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo-name.git
