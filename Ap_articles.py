import pandas as pd
from datetime import datetime
import time
from nltk.stem import PorterStemmer

class Article:
    all_articles = []  # Class level list to store all articles
    index_title = []
    index_excerpt = []
    total_articles = 0

    def __init__(self, date="", link="", title="", core_message="", excerpt="", suggested_by=""):
        self.date = date
        self.link = str(link)
        self.title = str(title)
        self.core_message = str(core_message)
        self.excerpt = excerpt
        self.suggested_by = suggested_by
        self.index_title = Counter()
        self.index_excerpt = Counter()
        self.total_words = len(str(self.excerpt).split())

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

    def prepare_index(self):
        """Precompute stemmed, lowercase searchable words for fast lookup."""
        title_words = [ps.stem(word) for word in str(self.title).lower().split()]
        self.index_title = Counter(title_words)
        excerpt_words = [ps.stem(word) for word in str(self.excerpt).lower().split()]
        self.index_excerpt = Counter(excerpt_words)
        self.index_combined = Counter(title_words + excerpt_words)

    @classmethod
    def add_articles(cls, file_path):

        # Load base data of articles
        df = pd.read_csv(file_path)

        for i, row in df.iterrows():

            # Cleanup date
            try:
                date = datetime.strptime(str(row['Date']), "%m/%d/%Y")
            except ValueError:
                date = None

            # Clean up link
            link = str(row['Link'])
            if not link.startswith("http://" or "/https:") and link != "":
                link = "http://" + link

            # Create an object of Article class with the data
            article_obj = Article(
                date=date,
                link=link,
                title=row["Title"],
                core_message=row["Core Message"],
                excerpt=row["Excerpt"],
                suggested_by=row["Suggested By"]
            )

            cls.all_articles.append(article_obj)  # Add a single object to the class-level list
            article_obj.prepare_index()

        Article.total_articles = len(Article.all_articles)
        # Print all article objects
        print(f"Searched in {len(Article.all_articles)} articles.")
from collections import Counter
ps = PorterStemmer()


file_path = '/Users/snehadhandhania/Code/Ap_Articles/For You Articles.csv'
Article.add_articles(file_path)

# remove words from search string that should not be searched
ignore_dict = {
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

ignore_words = {ps.stem(word) for category in ignore_dict.values() for word in category}


def keyword_search(keywords: str, time: datetime = datetime.now()):
    """Search for keywords across all articles and return the top matching links."""
    if time is None:
        time = datetime.now()

    # 1. Filter time relevant articles
    time_selected_articles = []
    for article in Article.all_articles:
        if article.date and article.date> time:
            time_selected_articles.append(article)

    if not time_selected_articles:
        print("No articles found in the selected time range.")
        return {"top_articles": [], "total_matched_articles": 0}

    number_of_links = 3 #Number of articles to be returned to the user

    #Preprocess keywords
    keywords_clean = [ps.stem(word) for word in
                      (keywords.lower().split())]  # Split search string into separate keywords
    keyword_index = Counter(keywords_clean)

    article_score = Counter()
    ##Inverted index Search
    inverted_index = {}
    for article in time_selected_articles:
        for word, count in article.index_excerpt.items():
            inverted_index.setdefault(word, {})[article.title]= count
    for keyword, qcount in keyword_index.items():
        for word2 in inverted_index:
            if keyword != word2:
                continue
            posting = inverted_index[keyword]
            for title, doc_freq in posting.items():
                article_score[title] += doc_freq*qcount

    print(article_score)
    sorted_articles = sorted(article_score.items(), key=lambda x: x[1], reverse=True)



    # #Calculate TF: Number of times a keyword appears in this article/total number of words in this article
    # TF = []
    # IDF_den = Counter()
    # for article in time_selected_articles:
    #         for keyword in keyword_index:
    #             if keyword in ignore_words:
    #                 continue
    #             keyword_count = article.index_combined.get(keyword,0)
    #             TF.append({"Keyword": keyword, "Article": article.title, "TF": keyword_count/article.total_words})
    #             if keyword_count >0:
    #                     IDF_den [keyword] +=1
    # total_matched_articles = 0  # number of articles with a search hit
    #
    # # Calculate IDF: log(Total # articles/number of articles in which the keyword appears) and TFIDF
    # idf = []
    # tfidf = []
    #
    # for keyword in keywords_clean:
    #     if IDF_den [keyword]>0:
    #         idf_value = math.log(len(time_selected_articles) / IDF_den[keyword])
    #     else:
    #         idf_value = 0
    #
    #     idf.append({"Keyword": keyword, "IDF": idf_value})
    #
    #     for article in time_selected_articles:
    #         tf_value = 0.0
    #         tf_value = next((item["TF"] for item in TF if item["Keyword"] == keyword and item["Article"] == article),
    #                         0.0)
    #         tfidf.append(
    #             {"Keyword": keyword, "Title": article.title, "Link": article.link, "TFIDF": tf_value * idf_value})
    #
    # ##Cosine similarity method
    # # Compute keyword vector
    # keyword_vector = {}
    # articles_vector = []
    #
    # # Compute keyword vector
    # for keyword in keyword_index:
    #     TF = keyword_index[keyword] / len(keywords_clean)
    #     IDF = next(item["IDF"] for item in idf if item["Keyword"] == keyword)
    #     keyword_vector[keyword] = TF * IDF
    #
    # # Compute article vector
    # for article in Article.all_articles:
    #     current_vector = []
    #
    #     for word in article.index_excerpt:
    #         TF = article.index_excerpt[word] / article.total_words
    #         IDF = next((item["IDF"] for item in idf if item["Keyword"] == word), 0.0)
    #         current_vector.append({"Word": word, "TFIDF": TF * IDF})
    #
    #     articles_vector.append({"Article": article, "Vector": current_vector})
    #
    # # Compute cosine similarity
    # # Compute magnitude of keyword and articles
    #
    # keyword_mag = math.sqrt(sum(v ** 2 for v in keyword_vector.values()))
    #
    # article_mag = []
    # for article in articles_vector:
    #     article_mag_value = 0
    #     for word in article["Vector"]:
    #         article_mag_value += word["TFIDF"] ** 2
    #
    #     article_mag.append({"Article": article, "Mag": article_mag_value ** 0.5})
    #
    # # Compute cosine of each article and keyword vector
    # cos_list = []
    #
    # for article in articles_vector:
    #     dot_product = 0
    #     for vector in article["Vector"]:
    #         word = vector["Word"]
    #         if word in keyword_vector:
    #             dot_product += keyword_vector[word] * vector["TFIDF"]
    #
    #     current_article_mag = next((mag["Mag"] for mag in article_mag if mag["Article"] == article["Article"]), 0.0)
    #     epsilon = 1e-10
    #     cos = dot_product / ((keyword_mag + epsilon) * (current_article_mag + epsilon))
    #     cos_list.append({"Title": article["Article"].title, "Link": article["Article"].link, "Cosine": cos})
    #
    #     if cos > 0:
    #         total_matched_articles += 1
    #
    # # Normalize if cos >1
    # max_cos = max((item["Cosine"] for item in cos_list), default=1)
    # for item in cos_list:
    #     item["Cosine"] /= max_cos
    #
    # sorted_articles = sorted(cos_list, key=lambda x: x["Cosine"], reverse=True)
    #
    # # Sort articles by TFIDF
    # # sorted_articles = sorted(tfidf, key=lambda x: x["TFIDF"], reverse=True)  # Sort articles by frequency of keywords
    #
    # deduplicate articles
    # unique_articles = {}
    # for item in sorted_articles:
    #     title = item["Title"]
    #     if title not in unique_articles:
    #         unique_articles[title] = item  # first occurrence = highest TF-IDF kept
    # unique_sorted_articles = list(unique_articles.values())
    # # Take top N articles
    # top_articles = unique_sorted_articles[
    #     :min(number_of_links, total_matched_articles)]  # removes articles with 0 match or when matches <number of links
    # return {"top_articles": top_articles, "total_matched_articles": total_matched_articles}


import math


start_time = time.time()
search_result = keyword_search("belief and/or loving", datetime(2025, 5, 31))
end_time = time.time()

# if search_result["total_matched_articles"] == 0:
#     print("Sorry! No relevant articles found. Try searching for something else.")
# else:
#     print(
#         f"Took {round(end_time - start_time, 5)} seconds to find {search_result['total_matched_articles']} relevant articles. Top articles are: ")
#
#     for i, art in enumerate(search_result["top_articles"], 1):
#         print(f" {i}. Article Title: {art['Title']}, Link: {art['Link']}, Cosine score is: {round(art['Cosine'], 2)} ")
