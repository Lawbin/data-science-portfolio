## happy path 1
* greet
  - utter_greet
  - utter_ask_movie

* inform{"movie_title":"3 Idiots"}
  - utter_random_response
  - action_recommendation_fromtable
  - action_search_movie
  - action_suggest_movie

* ask_plot
  - action_suggest_plot

* ask_comment
  - action_suggest_review

* thankyou
  - utter_thanks

* goodbye
  - utter_goodbye

## suggestion path
* ask_for_suggestion
  - utter_ask_movie

## challenge bot
* challenge_robot
  - utter_challenge

## out_of_scope
* out_of_scope
  - utter_backontrack