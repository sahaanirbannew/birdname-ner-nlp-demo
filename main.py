import spacy
import re 

def basic_preprocess(tweet):
  import preprocessor as p
  p.set_options(p.OPT.EMOJI, p.OPT.MENTION, p.OPT.URL, p.OPT.SMILEY, p.OPT.NUMBER,p.OPT.HASHTAG)
  tweet = tweet.lower()
  tweet = tweet.replace("\n"," ")  
  tweet = tweet.replace("\\n"," ")
  tweet = tweet.replace("'","") 
  tweet = p.clean(tweet)
  tweet = re.sub(r'[^\w\s]', ' ', tweet)
  tweet = re.sub(r' x..', '', tweet)
  tweet = re.sub(r' +', ' ', tweet) #' +', ' '
  #tweet = re.sub(r' n. ', '', tweet) 
  tweet = tweet.replace("x9c","")
  tweet = tweet.strip()
  return tweet

def app_run(sentence): 
  nlp_ner = spacy.load("model-best") 
  sentence = basic_preprocess(sentence)
  doc = nlp_ner(sentence)
  return (str(doc.ents))

from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello():
    return app_run("some nice asian koel songs here")
