import aylien_news_api
from aylien_news_api.rest import ApiException
from pprint import pprint
import copy
import dotenv
import json
import time
import requests

# %%
# Configure API key authorization: app_id
app_id = dotenv.get_key('../.env', 'AYLIEN_APP_ID')
app_key = dotenv.get_key('../.env', 'AYLIEN_APP_KEY')
endpoint = dotenv.get_key('../.env', 'AYLIEN_ENDPOINT')

configuration = aylien_news_api.Configuration()
configuration.api_key['X-AYLIEN-NewsAPI-Application-ID'] = app_id
configuration.api_key['X-AYLIEN-NewsAPI-Application-Key'] = app_key
configuration.host = endpoint

num_docs = 100
# %%
client = aylien_news_api.ApiClient(configuration)
api_instance = aylien_news_api.DefaultApi(client)


# %%
# Fetch stories using AYLIEN News API
def fetch_stories(opts, limit=None, append_to=None):
    fetched_stories = []
    stories = None
    counter = 0

    while stories is None or len(stories) == (opts.get('per_page') or 100):
        if limit and len(fetched_stories) >= limit:
            return fetched_stories
        try:
            response = api_instance.list_stories(**opts)
        except ApiException as e:
            if e.status == 429:
                if int(e.headers['x-ratelimit-volume-remaining']) == 0:
                    reset = e.headers('x-ratelimit-volume-reset')
                    print('Monthly rate limit exceeded. Wait until reset at %s' % reset)
                    return fetched_stories
                if int(e.headers['x-ratelimit-remaining']) == 0:
                    print('1-Minute rate limit exceeded. Waiting 60 seconds...')
                    time.sleep(60)
                    continue
            print("Exception when calling DefaultApi->list_stories: %s\n" % e)
            return fetched_stories

        if append_to:
            with open(append_to, 'a') as f:
                for story in response.stories:
                    sentiment_dict = {'body_polarity': story.sentiment.body.polarity if story.sentiment.body else None,
                                      'body_score': story.sentiment.body.score if story.sentiment.body else None,
                                      'title_polarity': story.sentiment.title.polarity if story.sentiment.title else None,
                                      'title_score': story.sentiment.title.score if story.sentiment.title else None}

                    source_dict = {
                        'description': story.source.description if story.source else None,
                        'discriminator': story.source.discriminator if story.source else None,
                        'domain': story.source.domain if story.source else None,
                        'home_page_url': story.source.home_page_url if story.source else None,
                        'id': story.source.id if story.source else None,
                        'links_in_count': story.source.links_in_count if story.source else None
                    }

                    story_dict = {'instance_id': counter, 'document_id': story.id, 'body': story.body, 'date': story.published_at.isoformat(),
                                  'sentiment': sentiment_dict, 'source': source_dict}
                    json.dump(story_dict, f, indent=4)
                    f.write(',')
                    counter += 1
                    print(counter)

        stories = response.stories
        opts['cursor'] = response.next_page_cursor

        fetched_stories += stories
        print(f'Fetched {len(stories)} stories. Total: {len(fetched_stories)} so far.')

        if fetched_stories == 1000:
            return fetched_stories

    return fetched_stories


# Alternate: Fetch stories using pure HTTP requests
def fetch_news(api_id, api_key, opts):
    base_url = 'https://api.aylien.com/news/stories'
    headers = {
        'X-AYLIEN-NewsAPI-Application-ID': api_id,
        'X-AYLIEN-NewsAPI-Application-Key': api_key
    }
    params = {
        'published_at.start': opts['published_at_start'],
        'published_at.end': opts['published_at_end'],
        # 'source_locations.country': ','.join(opts['source_locations_country']),
        # 'language': ','.join(opts['language']),
        'sort_by': opts['sort_by'],
        # 'sort_direction': opts['sort_direction'],
        'per_page': opts['per_page'],
    }
    if 'aql' in opts:
        params['aql'] = opts['aql']
    elif 'text' in opts:
        params['text'] = opts['text']

    response = requests.get(base_url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error when calling AYLIEN News API: {response.status_code}, {response.text}")
        return None


def match_bills(fetched_stories_file, bill_names_file, bill_matchings_file):
    fetched_stories = open(fetched_stories_file)
    fetched_stories = json.load(fetched_stories)

    bill_names = open(bill_names_file)
    bill_names = json.load(bill_names)

    match_count = 0

    for story in fetched_stories:
        id = story['instance_id']
        date = story['date']
        bill_matches = dict()

        # TODO: clean the bill names to match accurately

        for bill in bill_names.values():
            start_index = story['body'].find(bill['bill_number'])
            while start_index != -1:
                end_index = start_index + len(bill) - 1
                bill_matches[bill] = bill_matches.get(bill, []) + [(start_index, end_index)]
                start_index = story['body'].find(bill, end_index)

                story_matches = {'match_id': match_count, 'instance_id': id, 'bill_number': bill['bill_number'], 'start_index': start_index, 'end_index': end_index}

                with open(bill_matchings_file, 'a') as f:
                    json.dump(story_matches, f, indent=4)
                    f.write(",")

                match_count += 1



# %%
# generate AYLIEN Query Language (AQL, based on Lucene) query from keywords
keywords_file = '../models/story_keywords.txt'
with open(keywords_file, 'r') as f:
    keywords = f.read().splitlines()

climate_keywords_aql = 'text:(' + ' OR '.join([f'"{keyword}"' for keyword in keywords]) + ')'

# generate AQL query from bill info
bill_data_file = '../data/bill_data.json'
with open(bill_data_file, 'r') as f:
    bill_data = json.load(f)

bill_aql_tuples = [(f'"{bill["short_title"]}"', f'"{bill["bill_number"]}"') for bill in bill_data.values()]
half = len(bill_aql_tuples) // 2

bill_aql_1 = 'text:(' + ' OR '.join([st + ' OR ' + bn for st, bn in bill_aql_tuples[:half]]) + ')'
bill_aql_2 = 'text:(' + ' OR '.join([st + ' OR ' + bn for st, bn in bill_aql_tuples[half:]]) + ')'
# %%
# set options
opts_1 = {
    'aql': bill_aql_1,
    'published_at_start': 'NOW-27MONTH',
    'published_at_end': 'NOW-1DAY',
    'source_locations_country': ['US'],
    'language': ['en'],
    'sort_by': 'relevance',
    # 'sort_direction': 'asc',
    'per_page': 100,
}

opts_2 = copy.deepcopy(opts_1)
opts_2['aql'] = bill_aql_2
# %%
fetched = fetch_stories(opts_1, limit=10000, append_to='../data/fetched_stories.json')
match_bills('../data/fetched_stories.json', '../data/bill_data.json', '../data/bill_matchings.json')

# %%
def serializer(obj):
    if isinstance(obj, aylien_news_api.models.story.Story):
        return obj.to_dict()
    else:
        return str(obj)


with open('test.json', 'w') as f:
    json.dump(fetched, f, default=serializer, indent=4)
