import json
import keyboard
from spacy.lang.en import English
import numpy as np
import os

with open('../data/all_instances.json', 'r') as f:
    all_instances = json.load(f)

with open('../data/documents_bias.json', 'r') as f:
    documents = json.load(f)

# k-window is the number of tokens (k/2 before and k/2 after) to include in the instance
k = 50

# create tokenizer
nlp = English()
tokenizer = nlp.tokenizer

windows = {}

negative = []
neutral = []
positive = []

# iterate through instances and save k-window from corresponding document
for instance in all_instances:
    # get document id
    doc_id = str(instance['document_id'])
    # get document text
    doc_text = tokenizer(documents[doc_id]['body'].lower())
    # get start and end index of instance
    start = max(instance['start'] - k//2, 0)
    end = min(instance['end'] + k//2, len(doc_text))
    # get k-window from document text
    window = doc_text[start:end]
    # save window
    windows[instance['instance_id']] = window.text

    # get sentiment
    sentiment = documents[doc_id]['sentiment']['body_polarity']

    if sentiment == 'negative':
        negative.append(instance['instance_id'])
    elif sentiment == 'neutral':
        neutral.append(instance['instance_id'])
    elif sentiment == 'positive':
        positive.append(instance['instance_id'])


training_file = '../models/training_50.json'

if os.path.exists(training_file):
    with open(training_file, 'r') as f:
        training = json.load(f)
    training_keys = [t[0] for t in training]
else:
    training = []
    training_keys = []

# select a random sample of 8 negative, 16 neutral, and 8 positive instances
# (as classified by AYLIEN) that are not already in training
np.random.seed(50)
negative_new = set(negative) - set(training_keys)
neutral_new = set(neutral) - set(training_keys)
positive_new = set(positive) - set(training_keys)

training_keys += list(np.random.choice(list(negative_new), 16, replace=False)) \
                + list(np.random.choice(list(neutral_new), 8, replace=False))

# shuffle instances
np.random.shuffle(training_keys)
training = [(key, windows[key]) for key in training_keys]

# save training to file
with open('../models/training_new_emma.json', 'w') as f:
    json.dump(training, f)