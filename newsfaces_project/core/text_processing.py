import re
import json
from bs4 import BeautifulSoup
from langdetect import detect
import spacy
from keybert import KeyBERT
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer


class TextMetadataExtractor:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            self.nlp = None
        try:
            self.kw_model = KeyBERT()
        except Exception:
            self.kw_model = None
        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis")
        except Exception:
            self.sentiment_analyzer = None

        self.topic_keywords = {
            "politics": ["government", "election", "president", "minister", "policy", "vote"],
            "sports": ["game", "team", "player", "match", "score", "championship", "football"],
            "technology": ["software", "computer", "internet", "digital", "AI", "tech", "innovation"],
            "business": ["company", "market", "economy", "financial", "investment", "profit"],
            "entertainment": ["movie", "music", "celebrity", "film", "show", "actor"],
            "health": ["health", "medical", "doctor", "hospital", "disease", "treatment"],
            "science": ["research", "study", "science", "discovery", "experiment"],
            "education": ["school", "university", "student", "learning", "teacher"]
        }

    def clean_html_text(self, html_content):
        """Extract title and cleaned text."""
        if isinstance(html_content, bytes):
            html_content = html_content.decode("utf-8", errors="ignore")

        soup = BeautifulSoup(html_content, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
            tag.decompose()

        title_tag = soup.find("title")
        title = title_tag.get_text().strip() if title_tag else ""

        body_text = soup.get_text(separator="\n")
        cleaned = re.sub(r'\s+', ' ', body_text).strip()
        return {"title": title, "cleaned_text": cleaned}

    def detect_language(self, text):
        try:
            return detect(text[:1000]) if text and len(text.strip()) >= 10 else "unknown"
        except Exception:
            return "unknown"

    def extract_named_entities(self, text):
        if not self.nlp or not text:
            return [], [], []
        doc = self.nlp(text[:1000000])
        persons, orgs, locations = [], [], []
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                persons.append(ent.text)
            elif ent.label_ in ("ORG", "ORGANIZATION"):
                orgs.append(ent.text)
            elif ent.label_ in ("GPE", "LOC", "LOCATION"):
                locations.append(ent.text)

        def dedup(seq):
            seen, out = set(), []
            for x in seq:
                if x not in seen:
                    out.append(x)
                    seen.add(x)
            return out

        return dedup(persons), dedup(orgs), dedup(locations)

    def extract_keywords(self, text, num_keywords=8):
        if not text or len(text.strip()) < 50:
            return []
        try:
            if self.kw_model:
                kws = self.kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words="english", top_n=num_keywords)
                return [k[0] for k in kws]
        except Exception:
            pass
        try:
            vectorizer = TfidfVectorizer(max_features=200, stop_words="english", ngram_range=(1, 2))
            X = vectorizer.fit_transform([text])
            feat = vectorizer.get_feature_names_out()
            scores = X.toarray()[0]
            idx = scores.argsort()[-num_keywords:][::-1]
            return [feat[i] for i in idx if scores[i] > 0]
        except Exception:
            return []

    def analyze_sentiment(self, text):
        if not text or not self.sentiment_analyzer:
            return "neutral", 0.0
        try:
            sample = text[:512]
            result = self.sentiment_analyzer(sample)[0]
            label = result["label"].lower()
            score = float(result["score"])
            if label.startswith("pos"):
                return "positive", score
            elif label.startswith("neg"):
                return "negative", score
            return "neutral", score
        except Exception:
            return "neutral", 0.0

    def classify_topic(self, text, title=""):
        combined = f"{title} {text}".lower()
        best, best_score = "general", 0.0
        for topic, kws in self.topic_keywords.items():
            count = sum(1 for kw in kws if kw.lower() in combined)
            score = count / len(kws) if kws else 0
            if score > best_score:
                best, best_score = topic, score
        return best, best_score

    def process_text_metadata(self, html_content, metadata=None):
        cleaned = self.clean_html_text(html_content)
        title = cleaned["title"]
        cleaned_text = cleaned["cleaned_text"]

        language = self.detect_language(cleaned_text)
        keywords = self.extract_keywords(cleaned_text)
        persons, orgs, locations = self.extract_named_entities(cleaned_text)
        sentiment_label, sentiment_score = self.analyze_sentiment(cleaned_text)
        topic_category, _ = self.classify_topic(cleaned_text, title)

        return {
            "target_uri": metadata.get("target_uri") if metadata else None,
            "title": title,
            "cleaned_text": cleaned_text,
            "language": language,
            "sentiment_label": sentiment_label,
            "sentiment_score": sentiment_score,
            "topic_category": topic_category,
            "keywords": keywords,
            "person_entities": persons,
            "org_entities": orgs,
            "location_entities": locations
        }
