from flask import Flask, render_template, request
import joblib
import re
import string
import nltk

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("omw-1.4")



# Create Flask app
app = Flask(__name__)

# Load model and vectorizer
model = joblib.load("model/phishing_model.pkl")
vectorizer = joblib.load("model/tfidf_vectorizer.pkl")

# Initialize NLP tools
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

# Preprocessing function
def preprocess_text(text):

    text = text.lower()

    text = re.sub(r"http\\S+|www\\S+", "", text)
    text = re.sub(r"\\S+@\\S+", "", text)
    text = re.sub(r"\\d+", "", text)

    text = text.translate(str.maketrans("", "", string.punctuation))

    words = text.split()

    words = [
        lemmatizer.lemmatize(word)
        for word in words
        if word.isalpha() and word not in stop_words
    ]

    return " ".join(words)

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# Prediction
@app.route("/predict", methods=["POST"])
def predict():

    email = request.form["email"]

    processed = preprocess_text(email)

    vector = vectorizer.transform([processed])

    prediction = model.predict(vector)[0]

    if prediction == 1:
        result = "🚨 Phishing Email"
    else:
        result = "✅ Legitimate Email"

    return render_template("result.html",
                           prediction=result,
                           email=email)

# Run application
if __name__ == "__main__":
    app.run(debug=True)