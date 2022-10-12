import spacy
import re 
import os
import sys
import requests
import pickle
import pandas as pd
from flask import Flask, request, render_template
ON_HEROKU = os.environ.get('ON_HEROKU')
#from googlesearch import search 
import urllib.request
import html.parser 
from requests.exceptions import HTTPError
from socket import error as SocketError
from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor
import shutil

try:
  from bs4 import BeautifulSoup
except:
  print("issue here")



spelling_corrections = {}
spelling_corrections["grey"] = "gray" 
spelling_corrections["pegion"] = "pigeon" 
spelling_corrections["brested"] = "breasted" 
spelling_corrections["serpant"] = "serpent" 
spelling_corrections["avedavat"] = "avadavat" 
spelling_corrections["open billed stork"] = "asian openbill" 
spelling_corrections["secretary bird"] = "Secretarybird" 
spelling_corrections["dollar bird"] = "dollarbird"
spelling_corrections["eyes"] = "eye"


def return_html_code(url):
  opener = build_opener(HTTPCookieProcessor())
  response = opener.open(url)
  html = response.read() 
  return html

def load_all_birds_list(response):
  try:
    file = open("bird_list_df",'rb')
    bird_list_df = pickle.load(file)
    all_birds = bird_list_df["bird_name"].tolist()
    response["messages"].append("bird_list_df loaded") 
    try: 
      return all_birds, response
    except Exception as e:
      response["error"].append(str(e)) 
  except Exception as e: 
    response["error"].append(str(e)) 

def get_eBird_commonNames_data():
  file = open("bird_dict_comName",'rb')
  try:
    eBird_commonNames_data = pickle.load(file)
    return eBird_commonNames_data 
  except Exception as e:
    print(str(e))
    return 0
  
def return_eBird_list(spelling_corrections):
  eBird_commonNames = get_eBird_commonNames_data()
  eBird_commonNames_list = []
  for eBird in eBird_commonNames:
    if eBird_commonNames[eBird] != "ou":
      eBird_commonNames[eBird] = basic_preprocess(eBird_commonNames[eBird],spelling_corrections)
      eBird_commonNames_list.append(eBird_commonNames[eBird].strip())
  return eBird_commonNames_list

def root_path():
    # Infer the root path from the run file in the project root (e.g. manage.py)
    fn = getattr(sys.modules['__main__'], '__file__')
    root_path = os.path.abspath(os.path.dirname(fn))
    return root_path
  
def app_run(sentence,spelling_corrections):  #fetches bird by custom ner. 
  try:
    result = []
    nlp_ner = spacy.load("model-best") 
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
  response["bird-wiki"] = []    #birds found by rule based - wikipedia list.
  response["bird-ner"] = []     #birds found by ner 
  response["bird-ebird"] = []   #birds found by rule based - ebird list.
  response["error"] = []        #logs error texts
  response["messages"] = []     #saves messages to track things.
  
  try:
    all_birds, response = load_all_birds_list(response)   #loads list of all birds; around 11,000 of them. 
    response["messages"].append("all birds loaded") 
    response["messages"].append(str(len(all_birds)) + " birds list loaded.")
  except Exception as e: 
    response["error"].append(str(e))    #in case the file is not found.  
    
  try: 
    ebird_list = return_eBird_list(spelling_corrections)
  except Exception as e:
    response["error"].append(str(e))    #in case the file is not found.  
  
  try:
    sent_ = request.args.get('sent') #fetches the text via the argument.  
    response["messages"].append("user input recorded.")
      
    sent_ = " "+sent_+" " #owl-owlet problem. Pads the input string with one space.
    response["messages"].append("user input processed.")
    
    for bird in all_birds:            #no chances of error here. 
      bird = " "+bird+" " 
      bird_s = " "+bird+"s"            #munia - munias problem #this is no more required. 
      if sent_.find(bird) >-1 or sent_.find(bird_s) >-1:
        response["bird-wiki"].append(bird.strip())  #if bird is found by rule matching from wikipedia link, it is appended.
    
    for bird_ in ebird_list: 
      bird_ = " "+bird_+" "
      bird_s = " "+bird_+"s"            #munia-munias problem #this is no more required. 
      if sent_.find(bird_) >-1 or sent_.find(bird_s) >-1:
        response["bird-ebird"].append(bird_.strip()) #from the ebird list of birds.
       
    response["bird-ner"] = app_run(sent_,spelling_corrections) #if bird is found by ner, it is appended. 
    #why am i again preprocessing it inside app_run? sent_ is already processed. 
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
