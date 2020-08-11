from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
import requests
import json
import random
import re
import numpy as np
import pandas as pd

from scipy.spatial.distance import euclidean
from scipy.spatial.distance import cosine
from scipy.spatial.distance import correlation
from scipy.spatial.distance import hamming

df_imdb = pd.read_csv('./df_imdb.csv')
df_imdb__normalized = pd.read_csv('./df_imdb__normalized.csv')

def find_similar_movie(distance_method, movie_name, N):
    import random
    try:
        movie_id = df_imdb[df_imdb['title'].apply(lambda x: False if re.search(r"{}".format(movie_name),x,flags=re.IGNORECASE) == None else True)]['movie_id'].item()
    except:
        try:
            movie_id = df_imdb[df_imdb['title'].apply(lambda x: False if re.search(r"{}".format(movie_name),x,flags=re.IGNORECASE) == None else True)]['movie_id'][0]
        except:
            #random suggest a popular movie if cannot identify movie_name from user
            random_popular_ind = random.randint(0,19)
            movie_dict_popular = {"title":df_imdb.sort_values("rating",ascending=False).head(20).iloc[random_popular_ind,:]['title'],
                                  "url":df_imdb.sort_values("rating",ascending=False).head(20).iloc[random_popular_ind,:]['url']}
            return movie_dict_popular
        
    #create_new_dataframe containing the movie_id
    allMovies = pd.DataFrame(df_imdb__normalized.index,columns=["movie_id"])
    allMovies = allMovies[allMovies['movie_id']!= movie_id]
    allMovies["distance"] = allMovies['movie_id'].apply(lambda x: distance_method(df_imdb__normalized.loc[movie_id], df_imdb__normalized.loc[x]))
    TopNRecommendation = allMovies.sort_values(["distance"]).head(N)  
    
    recommend_movie_id_list = TopNRecommendation['movie_id'].values
    random_index = random.randint(0,len(recommend_movie_id_list)-1)
    recommend_movie_id = recommend_movie_id_list[random_index]
    new_df = df_imdb[df_imdb['movie_id'] == recommend_movie_id]
    
    movie_dict = {"title":new_df['title'].item(),"url":new_df['url'].item()}
    
    return movie_dict


class ActionRecommendation(Action):
    def name(self):
        return "action_recommendation_fromtable"

    def run (self, dispatcher, tracker, domain):
        recommend_movie = find_similar_movie(euclidean, tracker.get_slot("movie_title"),5)
        movie_title_fromtable = recommend_movie['title']
        movie_url_fromtable = recommend_movie['url']
        return[SlotSet('movie_title_fromtable',movie_title_fromtable),SlotSet('movie_url_fromtable',movie_url_fromtable)]

################################################################################################FROMAPI
class ActionSearchMovie(Action):
    def name(self):
        return "action_search_movie"

    def run (self, dispatcher, tracker, domain):

        headers = {
            'x-rapidapi-host': "imdb8.p.rapidapi.com",
            'x-rapidapi-key': "343116c3cdmsh22add87e617b792p16fa64jsnb5270f0532db"
            }

        # serarch for the movieID as the input of other API
        movieID_url = "https://imdb8.p.rapidapi.com/title/find"
        movieID_querystring = {"q":str(tracker.get_slot("movie_title_fromtable"))}
        movieid_response = requests.request("GET", movieID_url, headers=headers, params=movieID_querystring)
        movie_find = json.loads(movieid_response.text)

        movie_id = movie_find['results'][0]['id']
        movie_id = re.search('/title/(.*)/',movie_id).group(1)

        movie_title_suggest = movie_find['results'][0]['title']

        # search for the plot
        plot_url = "https://imdb8.p.rapidapi.com/title/get-plots"
        plot_querystring = {"tconst":str(movie_id)}
        plot_response = requests.request("GET", plot_url, headers=headers, params=plot_querystring)
        movie_plot=json.loads(plot_response.text)

        plot_list = []
        for i in movie_plot['plots']:
            try:
                plot_list.append(i['text'])   
            except:
                plot_list.append("Sorry, the plot is not available now.")

        random_plots_idx=random.randint(0,len(plot_list)-1)
        plot = plot_list[random_plots_idx]

        # search for movie review
        review_url = "https://imdb8.p.rapidapi.com/title/get-user-reviews"
        review_querystring = {"tconst":str(movie_id)}
        review_request = requests.request("GET", review_url, headers=headers, params=review_querystring)
        movie_review = json.loads(review_request.text)

        review_rating_list = [] 
        review_text_list = []
        review_title_list = []

        try:
            for i in movie_review['reviews']:
                try: 
                    review_rating_list.append(i['authorRating'])
                except:
                    review_rating_list.append('nan')
                try:
                    review_text_list.append(i['reviewText'])
                except:
                    review_text_list.append('Sorry, the review cannot be shown right now.')
                try:
                    review_title_list.append(i['reviewTitle'])
                except:
                    review_title_list.append('Unknown title')
            random_review_idx= random.randint(0,len(review_title_list)-1)
            review_title = review_title_list[random_review_idx]
            review_rating = review_rating_list[random_review_idx]
            review_text = review_text_list[random_review_idx]

        except:
            review_title = "Sorry. The title cannot be displayed."
            review_rating = "Rating not available."
            review_text = "The review is not available now."

        return [SlotSet('movie_title_suggest',movie_title_suggest),SlotSet('movie_id',movie_id),SlotSet('plot',plot),
                SlotSet('review_title',review_title),SlotSet('review_rating',review_rating),SlotSet('review_text',review_text)]

class ActionSuggestMovie(Action):
    def name(self):
        return "action_suggest_movie"

    def run (self,dispatcher,tracker,domain):
        dispatcher.utter_message(text = "Wait. Let me recommend you a movie.")
        dispatcher.utter_message(text = "How about " + str(tracker.get_slot('movie_title_suggest')) + " ?") 
        dispatcher.utter_message(text = "Check out more on the link below.") 
        dispatcher.utter_message(text = tracker.get_slot('movie_url_fromtable'))
        return []

class ActionSuggestPlot(Action):
    def name(self):
        return "action_suggest_plot"

    def run (self,dispatcher,tracker,domain):
        dispatcher.utter_message(text = "This movie is about...")
        dispatcher.utter_message(text = tracker.get_slot('plot'))
        return []

class ActionSuggestReview(Action):
    def name(self):
        return "action_suggest_review"

    def run (self,dispatcher,tracker,domain):
        dispatcher.utter_message(text = "I found some review on the internet as well.")
        dispatcher.utter_message(text = "Let me show you.")
        dispatcher.utter_message(text = tracker.get_slot('review_text'))
        return []



