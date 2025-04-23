from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon')

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text: str) -> float:
    return analyzer.polarity_scores(text)['compound']