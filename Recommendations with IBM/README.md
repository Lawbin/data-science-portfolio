# Recommendations with IBM

## Introduction
For this project we will analyze the interactions that users have with articles on the IBM Watson Studio platform, and make recommendations to them about new articles we think they will like. Below is an example of what the dashboard could look like displaying articles on the IBM Watson Platform.

![GitHub Logo](/data/image-1.png)

In order to determine which articles to show to each user, we will be performing a study of the data available on the IBM Watson Studio platform.

## Overview 

The notebook is divided into below parts:

### I. Exploratory Data Analysis

Before making recommendations of any kind, we will need to explore the data you are working with for the project.There are some basic, required questions to be answered about the data we are working with throughout the rest of the notebook.

### II. Rank Based Recommendations

To get started in building recommendations, we will first find the most popular articles simply based on the most interactions. Since there are no ratings for any of the articles, it is easy to assume the articles with the most interactions are the most popular. These are then the articles we might recommend to new users (or anyone depending on what we know about them).

### III. User-User Based Collaborative Filtering

In order to build better recommendations for the users of IBM's platform, we could look at users that are similar in terms of the items they have interacted with. These items could then be recommended to the similar users. This would be a step in the right direction towards more personal recommendations for the users.

### IV. Matrix Factorization

Finally, we will complete a machine learning approach to building recommendations. Using the user-item interactions, we will build out a matrix decomposition. Using our decomposition, we will get an idea of how well we can predict new articles an individual might interact with (spoiler alert - it isn't great). We will finally discuss which methods you might use moving forward, and how you might test how well your recommendations are working for engaging users.
