import pandas as pd
from datetime import datetime
import time
from nltk.stem import PorterStemmer

ps = PorterStemmer()
from collections import Counter
import math


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


file_path = '/Users/snehadhandhania/Code/Ap_Articles/For You Articles.csv'
Article.add_articles(file_path)


def keyword_search(keywords: str, time: datetime = datetime.now()):
    """Search for keywords across all articles and return the top matching links."""
    number_of_links = 3
    links = []
    # Clean up the search string
    keywords_clean = [ps.stem(word) for word in
                      (keywords.lower().split())]  # Split search string into separate keywords

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

    article_count_list = []  # Track total keyword hit in each article
    total_matched_articles = 0  # number of articles with a search hit
    number_of_docs_with_keyword = []
    tf = []
    idf = []
    tfidf = []


    for article in Article.all_articles:
        article_count = 0

        if time is None:
            time = datetime.now()

        if (article.date and article.date > time):  # Picks articles in the user's timeframe

            for keyword in keywords_clean:
                keyword_count = 0

                if keyword in ignore_words:
                    continue
                else:
                    # Count in title and excerpt
                    keyword_count += article.index_title.get(keyword, 0)
                    keyword_count += article.index_excerpt.get(keyword, 0)
                    article_count += article.index_title.get(keyword, 0)
                    article_count += article.index_excerpt.get(keyword, 0)
                    tf.append({"Keyword": keyword, "Article": article,
                               "tf": keyword_count / article.total_words})  # Number of times a keyword appears in this article/total number of words in this article
                    number_of_docs_with_keyword.append({"Keyword": keyword, "Article": article.title})

    # Calculate IDF
    for keyword in keywords_clean:

        df = Counter(
            item["Keyword"] for item in number_of_docs_with_keyword)  # Number of articles in which this keyword appears
        df_value = df.get(keyword, 1)
        idf_value = math.log(
            Article.total_articles / df_value)  # log(Total # articles/number of articles in which the keyword appears)
        idf.append(
            {"Keyword": keyword, "IDF": idf_value})

        for article in Article.all_articles:
            tf_value = 0.0
            tf_value = next((item["tf"] for item in tf if item["Keyword"] == keyword and item["Article"] == article),
                            0.0)
            tfidf.append(
                {"Keyword": keyword, "Title": article.title, "Link": article.link, "TFIDF": tf_value * idf_value})

    ##Cosine similarity method
    # Compute keyword vector
    keyword_vector = {}
    articles_vector = []

    query_counter = Counter(keywords_clean)
    for keyword in query_counter:
        TF = query_counter[keyword] / len(keywords_clean)
        IDF = next(item["IDF"] for item in idf if item["Keyword"] == keyword)
        keyword_vector[keyword] = TF * IDF

    # Compute article vector
    for article in Article.all_articles:
        current_vector = []

        for word in article.index_excerpt:
            TF = article.index_excerpt[word] / article.total_words
            IDF = next((item["IDF"] for item in idf if item["Keyword"] == word), 0.0)
            current_vector.append({"Word": word, "TFIDF": TF * IDF})

        articles_vector.append({"Article": article, "Vector": current_vector})

    # Compute cosine similarity

    # Compute magnitude of keyword and articles

    keyword_mag = math.sqrt(sum(v ** 2 for v in keyword_vector.values()))

    article_mag = []
    for article in articles_vector:
        article_mag_value = 0
        for word in article["Vector"]:
            article_mag_value += word["TFIDF"] ** 2

        article_mag.append({"Article": article, "Mag": article_mag_value ** 0.5})

    # Compute cosine of each article and keyword vector
    cos_list = []

    for article in articles_vector:
        dot_product = 0
        for vector in article["Vector"]:
            word = vector["Word"]
            if word in keyword_vector:
                dot_product += keyword_vector[word] * vector["TFIDF"]

        current_article_mag = next((mag["Mag"] for mag in article_mag if mag["Article"] == article["Article"]), 0.0)
        epsilon = 1e-10
        cos = dot_product / ((keyword_mag + epsilon) * (current_article_mag + epsilon))
        cos_list.append({"Title": article["Article"].title, "Link": article["Article"].link, "Cosine": cos})

        if cos > 0:
            total_matched_articles += 1

    # Normalize if cos >1
    max_cos = max((item["Cosine"] for item in cos_list), default=1)
    for item in cos_list:
        item["Cosine"] /= max_cos

    sorted_articles = sorted(cos_list, key=lambda x: x["Cosine"], reverse=True)

    # Sort articles by TFIDF
    # sorted_articles = sorted(tfidf, key=lambda x: x["TFIDF"], reverse=True)  # Sort articles by frequency of keywords

    # deduplicate articles
    unique_articles = {}
    for item in sorted_articles:
        title = item["Title"]
        if title not in unique_articles:
            unique_articles[title] = item  # first occurrence = highest TF-IDF kept
    unique_sorted_articles = list(unique_articles.values())
    # Take top N articles
    top_articles = unique_sorted_articles[
        :min(number_of_links, total_matched_articles)]  # removes articles with 0 match or when matches <number of links
    return {"top_articles": top_articles, "total_matched_articles": total_matched_articles}


start_time = time.time()
search_result = keyword_search("belief and/or loving", datetime(2025, 5, 31))
end_time = time.time()

if search_result["total_matched_articles"] == 0:
    print("Sorry! No relevant articles found. Try searching for something else.")
else:
    print(
        f"Took {round(end_time - start_time, 5)} seconds to find {search_result['total_matched_articles']} relevant articles. Top articles are: ")

    for i, art in enumerate(search_result["top_articles"], 1):
        print(f" {i}. Article Title: {art['Title']}, Link: {art['Link']}, Cosine score is: {round(art['Cosine'], 2)} ")
