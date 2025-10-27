from os import remove

import pandas as pd
from datetime import datetime
import time
from nltk.stem import PorterStemmer
ps = PorterStemmer()


class Article:
    all_articles = []  # Class level list to store all articles

    def __init__(self, date="", link="", title="", core_message="", excerpt="", suggested_by=""):
        self.date = date
        self.link = str(link)
        self.title = str(title)
        self.core_message = str(core_message)
        self.excerpt = excerpt
        self.suggested_by = suggested_by

    def __str__(self):
        if self.date:
            try:
                date_str = datetime.strptime(self.date, "%d-%m-%Y")
            except AttributeError:
                date_str = str(self.date)
        else:
            date_str = "Unknown date"

        # --- Make the link clickable (if terminal supports it) ---
        if self.link:
            clickable_link = f"\033]8;;{self.link}\033\\{self.link}\033]8;;\033\\"
        else:
            clickable_link = "No link available"

        return (
            f"ID: Date: {self.date} | Link: {clickable_link} | Title: {self.title} | Core_message: {self.core_message} | Excerpt: {self.excerpt} | Suggested_by: {self.suggested_by}")

    @classmethod
    def add_article(cls, article_obj):
        cls.all_articles.append(article_obj)  # Add a single object to the class-level list

#Load base data of articles
file_path = '/Users/snehadhandhania/Code/Ap_Articles/For You Articles.csv'
df = pd.read_csv(file_path)
print(df)

for i, row in df.iterrows():

    #Cleanup date
    try:
        date = datetime.strptime(str(row['Date']), "%m/%d/%Y")
    except ValueError:
        date = None

    #Clean up link
    link = str(row['Link'])
    if not link.startswith("http://" or "/https:") and link!="":
        link = "http://" + link

    #Create an object of Article class with the data
    article_obj = Article(
        date = date,
        link = link,
        title = row["Title"],
        core_message = row["Core Message"],
        excerpt = row["Excerpt"],
        suggested_by = row["Suggested By"]
    )

    #Create article object
    Article.add_article(article_obj)

#Print all article objects
print(f"Searched in {len(Article.all_articles)} articles.")


def keyword_search(keywords:str, time:datetime = datetime.now()):
    """Search for keywords across all articles and return the top matching links."""
    number_of_links = 3
    links = []
    # Clean up the search string
    keywords_clean = [ps.stem(word) for word in (keywords.lower().split())]  # Split search string into separate keywords
    # remove words from search string that should not be searched

    ignore_list = {
        "prepositions": [
            "in", "on", "at", "by", "for", "with", "about", "against", "between", "into", "through",
            "during", "before", "after", "above", "below", "to", "from", "up", "down", "over", "under",
            "again", "further", "then", "once", "of", "off", "around", "near"
        ],
        "conjunctions": [
            "and", "but", "or", "nor", "so", "for", "yet", "although", "because", "since", "unless",
            "while", "whereas", "after", "before", "once", "until", "when", "whenever"
        ],
        "articles": [
            "a", "an", "the"
        ],
        "pronouns": [
            "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "my",
            "your", "his", "their", "our", "mine", "yours", "hers", "ours", "theirs"
        ],
        "adjectives": [
            "good", "bad", "new", "old", "first", "last", "long", "short", "great", "small", "big",
            "high", "low", "young", "important", "different", "large", "few", "many", "same"
        ],
        "adverbs": [
            "very", "really", "just", "only", "too", "also", "well", "now", "then", "there", "here",
            "so", "as", "even", "ever", "still", "often", "usually"
        ],
        "auxiliary_verbs": [
            "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did"
        ],
        "punctuation_symbols": [
            ",", ".", ";", ":", "!", "?", "-", "--", "(", ")", "[", "]", "{", "}", "'", '"', "…",
            "’", "“", "”", "‘", "/", "\\", "|", "@", "#", "$", "%", "&", "*", "_", "+", "=", "<", ">", "`", "~"
        ]
    }

    ignore_words = (word for category in ignore_list.values() for word in category)

    article_count_list = []  # Track total keyword hit in each article
    total_matched_articles = 0 #number of articles with a search hit

    for article in Article.all_articles:
        article_count = 0

        if time is None:
            time = datetime.now()

        if(article.date and article.date > time): #Picks articles in the user's timeframe

            for keyword in keywords_clean:

                if keyword in ignore_words:
                    continue
                else:
                    # Count in title
                    for word in str(article.title).lower().split():
                        if ps.stem(word) == keyword:
                            article_count += 1

                    # Count in excerpt
                    for word in str(article.excerpt).lower().split():
                        if ps.stem(word) == keyword:
                            article_count += 1

            article_count_list.append({
                "title": article.title,
                "link": article.link,
                "count": article_count
            })
        
        if article_count > 0:
            total_matched_articles+=1
        
    # Sort articles by total keyword count
    sorted_articles = sorted(article_count_list, key=lambda x: x["count"],
                             reverse=True)  # Sort articles by frequency of keywords

    # Take top N articles

    top_articles = sorted_articles[:min(number_of_links, len(sorted_articles))]
    links = [article["link"] for article in top_articles]

    return {"top_articles": top_articles, "total_matched_articles": total_matched_articles}

start_time = time.time()
search_result=keyword_search("belief and/or loving", datetime(2025, 5, 31))
end_time = time.time()

print(f"Took {round(end_time-start_time,5)} seconds to find {search_result['total_matched_articles']} relevant articles. Top articles are: ")

for i, art in enumerate(search_result["top_articles"], 1):
    print(f" {i}. Article Title: {art['title']}, Link: {art['link']}, Matches: {art['count']}")

    

