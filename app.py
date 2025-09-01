# app.py (Fixed Resume Version)

import os
import re
import fitz
from flask import Flask, request, render_template
import spacy

# --- Load NLP and Resume at Startup ---
nlp = spacy.load("en_core_web_md")

def extract_text_from_pdf(pdf_path):
    # This function is the same as before
    # ...
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text")
        text = re.sub(r'\n+', '\n', text)
        return text
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return None

# --- Pre-load your resume's text into a global variable ---
RESUME_FILE = "my_resume.pdf" # Make sure this file exists in your project
RESUME_TEXT = extract_text_from_pdf(RESUME_FILE)

# The find_specific_experience and find_related_experience functions are the same
def find_specific_experience(resume_text, keyword):
    # ...
    if not resume_text or not keyword: return []
    sentences = re.split(r'(?<=[.?!])\s+', resume_text)
    found_sentences = []
    keyword_regex = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
    for sentence in sentences:
        cleaned_sentence = sentence.replace('\n', ' ').strip()
        if cleaned_sentence and keyword_regex.search(cleaned_sentence):
            found_sentences.append(cleaned_sentence)
    return found_sentences

def find_related_experience(resume_text, keyword):
    # ...
    if not resume_text or not keyword: return {}
    target_token = nlp(keyword)[0]
    doc = nlp(resume_text)
    similar_words = set()
    for token in doc:
        if token.has_vector and token.is_alpha and not token.is_stop:
            if target_token.similarity(token) > 0.7 and target_token.text.lower() != token.text.lower():
                similar_words.add(token.lemma_.lower())
    related_experiences = {}
    for word in similar_words:
        found_sentences = find_specific_experience(resume_text, word)
        if found_sentences:
            related_experiences[word] = found_sentences
    return related_experiences


# --- Create the Flask App ---
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    context = {}
    if request.method == 'POST':
        keyword = request.form.get('keyword', '').strip()
        if keyword:
            # Search the pre-loaded resume text
            context['exact_experiences'] = find_specific_experience(RESUME_TEXT, keyword)
            context['related_experiences'] = find_related_experience(RESUME_TEXT, keyword)
            context['keyword'] = keyword
        else:
            context['error'] = "Please enter a keyword."
            
    return render_template('index.html', **context)

if __name__ == '__main__':
    app.run(debug=True)