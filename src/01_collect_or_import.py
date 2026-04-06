"""imports or reads your raw dataset; if you scraped, include scraper here"""
## I used a scrapper, "https://www.linkedin.com/pulse/how-scrape-google-play-reviews-4-simple-steps-using-python-kundi/" was the scrapper I used.

from google_play_scraper import app, reviews
import pandas as pd
import numpy as np 
import json


from google_play_scraper import Sort, reviews_all


reviews_ca, _ = reviews(
    'com.getsomeheadspace.android',
    lang='en', # defaults to 'en'
    country='ca', # defaults to 'us'
    sort=Sort.NEWEST, # defaults to Sort.MOST_RELEVANT
    count = 5000
) 

df_busu = pd.DataFrame(np.array(reviews_ca),columns=['review'])

df_busu = df_busu.join(pd.DataFrame(df_busu.pop('review').tolist()))

df_busu.head() 

output_file = "data/reviews_raw.jsonl"
with open(output_file, "w", encoding="utf-8") as f:
    for i, review in enumerate(reviews_ca, start=1):        #Keep only relevant fields
        entry = {
            "ID": i, 
            "content": review.get("content"),
            "score": review.get("score"),
            "at": str(review.get("at"))  #convert datetime to string
        }

        json.dump(entry, f)
        f.write("\n")

print(f"Saved {len(reviews_ca)} reviews to {output_file}")