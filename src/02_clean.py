"""Clean raw review data and create cleaned dataset"""

import json
import re
from num2words import num2words

#import nltk
#nltk.download('stopwords')
#nltk.download('wordnet')
#nltk.download('omw-1.4')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


#Setup NLP tools
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

#Helper function to remove emojis from reviews. This particular helper function was implemented with the help of chatgpt. 

def remove_emojis(text):
    """Remove emojis using regex"""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"
        "\U0001F780-\U0001F7FF"
        "\U0001F800-\U0001F8FF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FAFF"
        "\U00002700-\U000027BF"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r'', text)

#Helper function that, given a text, converts all numerical numbers to their correspnding alphabetical words. Example: 2 gets converted to two.
def numbers_to_words(text):
    def replace_number(match):
        num = match.group()
        try:
            return num2words(int(num))
        except:
            return num
    return re.sub(r'\b\d+\b', replace_number, text)

#Funtion that cleans the raw reviews from the raw reviews json file. 
def clean_text(text):

    #Converts the text to lowercase
    text = text.lower()
    #Removes the emojis
    text = remove_emojis(text)
    #Converts numbers to their corresponding words
    text = numbers_to_words(text)
    #Removes punctuations & special characters
    text = re.sub(r'[^a-z\s]', ' ', text)
    #Removes extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    words = text.split()

    #Removes the stopwords and lemmatizes
    cleaned_words = [
        lemmatizer.lemmatize(word)
        for word in words
        if word not in stop_words
    ]
    #Puts it all back together
    return " ".join(cleaned_words)




input_file = "data/reviews_raw.jsonl"
output_file = "data/reviews_clean.jsonl"

dups = set()
cleaned_data = []

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        review_json = json.loads(line)

        #Extract fields
        unique_ID = review_json.get("ID")
        raw_text = review_json.get("content", "")
        score = review_json.get("score", None)
        date = review_json.get("at", None)

        #Skip empty
        if not raw_text or not raw_text.strip():
            continue

        #Removes duplicates
        if raw_text in dups:
            continue
        dups.add(raw_text)

        #Remove short reviews
        if len(raw_text.split()) < 10:
            continue

        #Clean the text
        cleaned_text = clean_text(raw_text)

        #Skip if cleaning removed everything
        if not cleaned_text:
            continue

        #Store cleaned text
        cleaned_entry = {
            "ID": unique_ID,
            "review": cleaned_text,
            "score": score,
            "date": str(date)
        }

        cleaned_data.append(cleaned_entry)



with open(output_file, "w", encoding="utf-8") as f:
    for entry in cleaned_data:
        json.dump(entry, f)
        f.write("\n")

print(f"Cleaning complete. Saved {len(cleaned_data)} reviews.")