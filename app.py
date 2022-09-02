import spacy
import re 
import os
import requests
import pickle
from flask import Flask, request, render_template
ON_HEROKU = os.environ.get('ON_HEROKU')

def load_all_birds_list():
  file = open("bird_list_df",'rb')
  bird_list_df = pickle.load(file)
  try: 
    return bird_list_df
  except:
    print("Error: No bird list found.")
    return 0
  
def acknowledgements():
  return "- thank you Abhishek Bora (student, Pune Institute of Computer Technology, India), Soham Basu (student, M.Sc. Freiburg, Germany)"



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
  tweet = re.sub(r' +', ' ', tweet) 
  tweet = tweet.replace("x9c","")
  tweet = tweet.strip()
  return tweet

def app_run(sentence):  #fetches bird by custom ner. 
  try:
    result = []
    nlp_ner = spacy.load("model-best") 
    sentence = basic_preprocess(sentence)
    doc = nlp_ner(sentence)
    for ent in doc.ents:
      result.append(str(ent))
    return result
  except Exception as e:
    return str(e)

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():        #landing page lol.
  try:
    return render_template('index.html')
  except Exception as e:
    return str(e) 
 
  
@app.route('/ner')        #This is the main program.  :3 
def send_ner():
  response = {}                 #helps us send json files. 
  response["bird-rule"] = []    #birds found by rule based.
  response["bird-ner"] = []     #birds found by ner 
  response["error"] = []        #logs error texts
  response["messages"] = []     #saves messages to track things.
  
  try:
    all_birds = load_all_birds_list()   #loads list of all birds; around 11,000 of them. 
    response["messages"].append("all birds loaded") 
    response["messages"].append(str(len(all_birds)), " birds list loaded.")
  except Exception as e: 
    response["error"].append(str(e))    #in case the file is not found. 
  
  try:
    sent_ = request.args.get('sent')  #fetches the text via the argument. 
    response["messages"].append("user input recorded.")
      
    sent_ = basic_preprocess(sent_)   #preprocessing pipeline.
    response["messages"].append("user input processed.")
    
    for bird in all_birds:            #no chances of error here. 
      if sent_.find(bird) >-1:
        response["bird-rule"].append(bird)  #if bird is found by rule matching, it is appended.
    
    response["bird-ner"] = app_run(sent_) #if bird is found by ner, it is appended. 
  except Exception as e:
    response["error"].append(str(e)) 
  return response
  
  
if __name__ == '__main__':
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    
    if ON_HEROKU:
      port = int(os.environ.get('PORT', 17995))  # as per OP comments default is 17995
    else:
      port = 3000
    app.run(debug=True, port = port)
