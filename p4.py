import os
import re
import string
import requests
import numpy as np
import nltk
import spacy
from flask import Flask, request, render_template
from bs4 import BeautifulSoup
from keras.models import load_model
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from googleapiclient.discovery import build

# Set API key and Search Engine ID
api_key = os.getenv("GOOGLE_API_KEY", "YOUR_API_KEY")  # Replace with your actual API key
search_engine_id = os.getenv("GOOGLE_CSE_ID", "YOUR_CX_ID")  # Replace with your actual CX ID

# Ensure the model file exists
if not os.path.exists("p.h5"):
    raise FileNotFoundError("Error: 'p.h5' file is missing. Please add it to the project directory.")

# Load Keras model
model = load_model("p.h5")

# ✅ Load spaCy's medium model (Replacing `place.kv`)
nlp = spacy.load("en_core_web_md")
stop_words = nlp.Defaults.stop_words

# Flask App
app = Flask(__name__)

# ✅ Tokenizer function using spaCy
def spacy_tokenizer(sentence):
    doc = nlp(sentence)
    mytokens = [word.lemma_.lower().strip() for word in doc]
    mytokens = [word for word in mytokens if word not in stop_words and word not in string.punctuation]
    return mytokens

# ✅ Convert sentence to vector using spaCy (Replaces `place.kv`)
def sent_vec(sent):
    """Convert a sentence into a vector using spaCy."""
    doc = nlp(" ".join(sent))  # Join words into a sentence and convert to vector
    return doc.vector  # Return spaCy's dense vector

# ✅ Function to fetch similar articles from Google Custom Search API
def getSimilarArticles(input_text):
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": " ".join(input_text),  # Ensure input is a single string
        "cx": search_engine_id,
        "key": api_key,
    }

    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()

        if "items" not in data:
            print("⚠️ No search results found.")
            return "Error", "N/A"

        results = data["items"]
        first_result = results[0]
        return first_result["title"], first_result["link"]

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching articles: {e}")
        return "Error", "N/A"

# Extract URLs from text
def extract_urls(text):
    url_pattern = re.compile(r"https?://\S+")
    urls = re.findall(url_pattern, text)
    print("Extracted URLs:", urls)
    return urls

# Home route
@app.route("/")
def index():
    return render_template("index.html")

# ✅ Handling form submission (Fixed Invalid URL Error)
@app.route("/", methods=["POST"])
def output():
    input1 = request.form.get("input1", "").strip()
    input2 = request.form.get("input2", "").strip()

    if input1:
        url_match = re.search(r"(https?://\S+)", input1)

        if url_match and len(url_match.group(0)) == len(input1):
            return render_template("index.html",
                                   content="Not Possible",
                                   ip_text=input1,
                                   is_similar_search=False,
                                   similar_search_link="NA")

        result, similar_article_url = getSimilarArticles(spacy_tokenizer(input1))
        is_similar_search = similar_article_url != "N/A"

        # ✅ Fix: Ensure `result` is a valid URL before making a request
        if result == "Error" or not result.startswith("http"):
            print(f"⚠️ Error: getSimilarArticles() returned an invalid result: {result}")
            return render_template("index.html",
                                   content="Could not fetch a valid article. Try another input.",
                                   ip_text=input1,
                                   is_similar_search=False,
                                   similar_search_link="NA")

    elif input2:
        if re.search(r"(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])", input2):
            return render_template("index.html",
                                   content="Not Possible",
                                   ip_text=input2,
                                   is_similar_search=False,
                                   similar_search_link="NA")

        return render_template("index.html",
                               content="Not Possible",
                               ip_text=input2,
                               is_similar_search="Not Possible",
                               similar_search_link="None")

    else:
        return render_template("index.html",
                               content="Not Possible",
                               ip_text="",
                               is_similar_search=False,
                               similar_search_link="None")

    # ✅ Fetch and process news content correctly
    try:
        response = requests.get(result)
        response.raise_for_status()  # Check if the request is successful
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error fetching article content: {e}")
        return render_template("index.html",
                               content="Failed to retrieve the article.",
                               ip_text=input1,
                               is_similar_search=False,
                               similar_search_link="NA")

    html_content = response.content
    doc = BeautifulSoup(html_content, "html.parser")

    # ✅ Extract text properly
    text_full = " ".join([tag.text.strip() for tag in doc.find_all("p", recursive=False)])
    if not text_full:
        return render_template("index.html",
                               content="No valid news content found.",
                               ip_text=input1,
                               is_similar_search=False,
                               similar_search_link="NA")

    # ✅ Convert text into vector & predict
    tokenized_text = spacy_tokenizer(text_full)
    vectorized_text = sent_vec(tokenized_text).reshape((1, 300))

    t = model.predict(vectorized_text)
    answer = "True News" if np.round(t) == 1 else "False News"

    return render_template("index.html",
                           content=answer,
                           ip_text=input1,
                           is_similar_search=is_similar_search,
                           similar_search_link=similar_article_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
