import sys

import nltk
nltk.download(['punkt', 'wordnet'])

import re
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score

import pickle

from sqlalchemy import create_engine

def load_data(database_filepath):
    """
    Load cleaned data from database into dataframe.
    
    Args:
        database_filepath: String. It contains cleaned data table.
        
    Returns:
        X: DataFrame. Disaster messages.
        y: DataFrame. Disaster categories for each messages.
        category_names: list. Disaster category names.
    """
    engine = create_engine('sqlite:///{}'.format(database_filepath))
    df = pd.read_sql_table('messages', con=engine)
    
    X = df['message']
    y = df.drop(columns = ['message', 'genre', 'id', 'original'])
    category_names = list(y.columns)
    
    return X, y, category_names


def tokenize(text):
    '''
    Args:
        text: String. A disaster message.
        
    Returns:
        tokens: list of strings. A list of strings containing normalized and stemmed tokens.
    '''
    url_regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    
    # Get list of urls using regex
    detected_urls = re.findall(url_regex, text)
    
    # Replace each url in text with a placeholder
    for url in detected_urls:
        text = text.replace(url, 'urlplaceholder')
    
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()
    
    clean_tokens = []
    
    # Iterate through each token. Lemmatize, normalize case and remove leading/trailing white space
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)
        
    return clean_tokens

def build_model():
    """
    Builds a ML pipeline and performs GridSearch.
    
    Args:
        None
        
    Returns:
        cv: GridSearchCV object.
    """
    
    pipeline = Pipeline([
    ('vect', CountVectorizer(tokenizer=tokenize)),
    ('tfidf', TfidfTransformer()),
    ('clf', MultiOutputClassifier(
        RandomForestClassifier(
            n_estimators = 200,
            random_state = 42)
        ))
    ])
    
    parameters = {'tfidf__use_idf': (True, False),
              'clf__estimator__n_estimators': [50, 100], 
              'clf__estimator__random_state': [42]}

    cv = GridSearchCV(pipeline, param_grid = parameters, n_jobs = -1)
    return cv


def evaluate_model(model, X_test, y_test, category_names):
    """
    Returns test accuracy, number of 1s and 0s, recall, precision and F1 Score.
    
    Args:
        model: model object.
        X_test: pandas dataframe containing test features.
        y_test: pandas dataframe containing test labels.
    
    Returns:
        None.
    """
    
    y_pred = model.predict(X_test)
    
    i = 0
    for col in y_test:
        print('Feature {}: {}'.format(i+1, col))
        print(classification_report(y_test[col], y_pred[:, i]))
        i = i + 1
    accuracy = (y_pred == y_test.values).mean()
    print('The model accuracy is {:.3f}'.format(accuracy))


def save_model(model, model_filepath):
    '''
    Save model as a pickle file; converting into a byte stream.
    
    Args:
        model: model object.
        model_filepath: String. Path to where model is located.
    
    Returns:
        None.
    '''
    with open(model_filepath, 'wb') as file:
        pickle.dump(model, file)


def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, y, category_names = load_data(database_filepath)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, y_test, category_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()