#%%
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from app.recommender.utils_sent import rescale, round_of_rating

#%%
def sentiment_analyzer_scores(sentence, scale_bottom = 0, scale_top = 5):
    analyser = SentimentIntensityAnalyzer()
    sentiment_dict = analyser.polarity_scores(sentence)
    return round_of_rating(rescale(sentiment_dict['compound'], new_min = scale_bottom, new_max = scale_top))
