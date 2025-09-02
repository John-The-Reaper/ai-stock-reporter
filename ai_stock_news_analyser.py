import requests
import json
from datetime import datetime
import google.generativeai as genai
import os
import yfinance as yf



# Configuration de l'API Alpha Vantage
API_KEY = ""  # Remplacez par votre clé API gratuite d'Alpha Vantage
BASE_URL = "https://www.alphavantage.co/query"

def get_company_news(ticker, limit=5, api_key=API_KEY):
    """
    Récupère les actualités récentes pour une entreprise via Alpha Vantage.
    :param ticker: Symbole boursier de l'entreprise (ex: 'AAPL' pour Apple)
    :param limit: Nombre maximum d'actualités à retourner
    :return: Liste des actualités formatées
    """
    
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": ticker,
        "apikey": api_key,
        "limit": limit
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()  
    data = response.json()

    news_feed = data["feed"][:limit]

    formatted_news = [
        {
            "title": article.get("title", "Sans titre"),
            "date": datetime.strptime(
                article.get("time_published", "19000101T000000"),
                "%Y%m%dT%H%M%S"
            ).strftime("%Y-%m-%d %H:%M:%S") if article.get("time_published") else "Date inconnue",
            "summary": article.get("summary", "Aucun résumé"),
            "sentiment": article.get("overall_sentiment_label", "Inconnu"),
            "url": article.get("url", "Aucun lien")
        }
        for article in news_feed
    ]

    with open(f"news_data_{ticker}_va.json", "w") as fp:
        json.dump(formatted_news, fp, indent=4)

    return formatted_news   

def get_latest_news(ticker, num):
    """
    id:
    content:
        title:
        description:
        summary:
        provider:

    
    """
    stock = yf.Ticker(ticker)
    news = stock.get_news(count=num, tab='news')
    news_data = []

    analyst_price_target = stock.analyst_price_targets
    keys = news[0]

    for i in range(0,num):
        news_data.append({
            'id':news[i]['id'],
            'title':news[i]['content']['title'],
            'description':news[i]['content']['description'],
            'summary':news[i]['content']['summary'],
            'provider':news[i]['content']['provider']
        })
    news_data.append({'price_target':analyst_price_target})

    with open(f"news_data_{ticker}_yf.json", "w") as fp:
        json.dump(news_data, fp, indent=4)

    return news_data

def read_json_files(file1_path, file2_path):
    with open(file1_path, 'r', encoding='utf-8') as file1:
        data1 = json.load(file1)
    
    with open(file2_path, 'r', encoding='utf-8') as file2:
        data2 = json.load(file2)
        
    return data1, data2

def get_company_news_ai(prompt: str):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

def main():
    # Demander à l'utilisateur le symbole boursier
    ticker = input("Entrez le symbole boursier de l'entreprise (ex: AAPL pour Apple) : ").upper()
    
    # Récupérer et afficher les 5 actualités les plus récentes
    news = get_company_news(ticker, limit=20)

    # Récupérer les actualités via yfinance
    news_yf = get_latest_news(ticker, 20)

    """
    Tu es un portfolio manager. Tu gères actuellement 1000 dollars. Ton obkectif est de déterminer ...
    Ton output sera sous la forme suivante :
    {
        tp: ...
        sl: ...
        entry: ...
        summary: ... # Résumé des raisons qui t'ont poussées à prendre ce trade, simple concise mais un minimum détaillées
    }


    """

    TICKER = ticker
    file1_path = f"news_data_{TICKER}_yf.json"
    file2_path = f"news_data_{TICKER}_va.json"

    data1, data2 = read_json_files(file1_path, file2_path)

    prompt = f"""
    Ci joint les dernières actualitées concernant l'entreprise : {TICKER}.
    Je souhaite que tu me fasse un résumé de ces analyses et que tu me donnes les points positifs et négatifs

    Voici les actualités :
    {data1}
    {data2}
    """

    genai.configure(api_key="")

    print(get_company_news_ai(prompt))



# Fusionner ce doc et get_vantage_news.py

if __name__ == "__main__":
    main()