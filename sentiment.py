import json
from textblob import TextBlob

def analyze_sentiment(json_file):
    with open(json_file, "r") as f:
        data = json.load(f)

    tweets = data["tweets"]
    total = len(tweets)
    pos = neu = neg = 0
    score = 0.0

    for tweet in tweets:
        blob = TextBlob(tweet)
        polarity = blob.sentiment.polarity
        score += polarity
        if polarity > 0.1:
            pos += 1
        elif polarity < -0.1:
            neg += 1
        else:
            neu += 1

    # Changed calculation to be more precise
    if total > 0:
        # Calculate base rating from 0-5 scale
        base_rating = 2.5 + (score / total) * 2.5
        # Adjust based on positive/negative ratio
        pos_ratio = pos / total if total > 0 else 0
        neg_ratio = neg / total if total > 0 else 0
        adjustment = (pos_ratio - neg_ratio) * 0.5
        final_rating = base_rating + adjustment
        
        # Ensure rating stays within 0-5 range and round to 2 decimal places
        final_rating = round(max(0, min(5, final_rating)), 2)
    else:
        final_rating = 2.50

    return {
        "positive": pos,
        "neutral": neu,
        "negative": neg,
        "rating": final_rating
    }