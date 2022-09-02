import spacy
import re 
import os
ON_HEROKU = os.environ.get('ON_HEROKU')

def acknowledgements():
  return "- thank you Abhishek Bora (student, College Pune India), Soham Basu (student, M.Sc. Freiburg, Germany"



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
  try:
    nlp_ner = spacy.load("model-best") 
    sentence = basic_preprocess(sentence)
    doc = nlp_ner(sentence)
    return (str(doc.ents))
  except Exception as e:
    return str(e)

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
  response_ = app_run("some nice asian koel songs here") +  acknowledgements()
  return response_
 
if __name__ == '__main__':
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    if ON_HEROKU:
    # get the heroku port
      port = int(os.environ.get('PORT', 17995))  # as per OP comments default is 17995
    else:
      port = 3000
    app.run(debug=True, port = port)
