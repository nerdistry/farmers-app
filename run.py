from main import app, db
from google.cloud import translate_v2 as translate
from flask import Flask, request, render_template, jsonify
import os
from jinja2 import Environment, FileSystemLoader

app = Flask(__name__)

# Initialize Google Cloud Translation client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "YOUR JSON FILE CONTAINING your google credentials"  
translation_client = translate.Client()
def translate_text(text, target_language):
    result = translation_client.translate(text, target_language=target_language)
    return result['translatedText']
app.jinja_loader = FileSystemLoader('templates')
def translate_filter(text):
    user_language = request.accept_languages.best_match(['en', 'es', 'fr', 'de']) 
    return translate_text(text, user_language)
env = app.jinja_env
env.filters['translate'] = translate_filter

@app.route('/')
def index():
    return render_template('index.html')
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)