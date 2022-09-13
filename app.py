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

def download_image(img_link, response):
  try:
    file_name=img_link.split("/")[len(img_link.split("/"))-1]
    ##file_name = url_for('static', filename=file_name)
    ##file_name = "/static/"+file_name
    #file_name = os.path.join(app.root_path, "static", file_name) 
    file_name = "/static/"+file_name
    res = requests.get(img_link, stream = True)
    if res.status_code == 200: 
      
      with open(file_name,'wb') as f:
          shutil.copyfileobj(res.raw, f)  
      f.close() 
      crop_resize_image(file_name)
      return file_name, response  
    
    else: return "", response
  except Exception as e:
    response['error'].append(str(e))
    print(str(e), img_link)
  return "", response

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


def basic_preprocess(tweet, spelling_corrections):
  import preprocessor as p
  p.set_options(p.OPT.EMOJI, p.OPT.MENTION, p.OPT.URL, p.OPT.SMILEY, p.OPT.NUMBER)
  tweet = tweet.lower()
  tweet = tweet.replace("\n"," ")  
  tweet = tweet.replace("\\n"," ")
  if tweet[:2] == "b'": tweet = tweet[1:] 
  tweet = tweet.replace("'","") 
  tweet = p.clean(tweet)
  tweet = re.sub(r'[^\w\s]', ' ', tweet)
  tweet = re.sub(r' x..', '', tweet)
  tweet = re.sub(r' +', ' ', tweet)  
  tweet = tweet.strip()
  for key in spelling_corrections: 
    if tweet.find(key)>-1: 
      tweet = tweet.replace(key,spelling_corrections[key])
  return tweet

def root_path():
    # Infer the root path from the run file in the project root (e.g. manage.py)
    fn = getattr(sys.modules['__main__'], '__file__')
    root_path = os.path.abspath(os.path.dirname(fn))
    return root_path
  
def app_run(sentence,spelling_corrections):  #fetches bird by custom ner. 
  try:
    result = []
    nlp_ner = spacy.load("model-best") 
    sentence = basic_preprocess(sentence,spelling_corrections)
    doc = nlp_ner(sentence)
    for ent in doc.ents:
      result.append(str(ent))
    return result
  except Exception as e:
    return str(e)

def search_speciesCode_by_commName(commName,bird_dict_comName):
  for key in bird_dict_comName:
    if bird_dict_comName[key] == commName.lower():
      return key
  return ""

def search_by_commonName_google(commonName): 
  results = search(commonName, tld="com", num=3, stop=3, pause=2) 
  for result in results: 
    if str(result).find("ebird.org") > -1:
      eBird_link = result
      speciesCode = eBird_link.split("/")[len(eBird_link.split("/"))-1]
      return speciesCode, eBird_link

def get_all_image_links(complete_dataset_dict, response):
  bird_for_gallery = {} 
  for key in complete_dataset_dict: 
    download_link = "" 
    count = 0 
    while download_link == "":
      download_link = complete_dataset_dict[key]["entries"][count]["media_url"] 
      count += 1
      if count == len(complete_dataset_dict[key]["entries"]):
        break
    if type(download_link) == str:  
      try:
        file_name,response = download_image(download_link,response) 
      except Exception as e: 
        response["error"].append(key+" :Download faild"+str(e))
      bird_for_gallery[key] = file_name
  return bird_for_gallery, response












from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():        #landing page lol.
  try:
    return render_template('index.html')
  except Exception as e:
    return str(e) 

@app.route('/gallery')
def gall():
  response={}
  response['message'] = []
  response['error'] = []
  
  try:
    dataset_dict_path = open("dataset_dictionary",'rb') 
    dataset_dict = pickle.load(dataset_dict_path)
    dataset_dict_path.close()
  except Exception as e: 
    response['error'].append("Loading Dataset: "+str(e))
# till here is fine! 

 # try: 
 #   gallery_images, response = get_all_image_links(dataset_dict,response)
 #   response['message'].append("Gallery images loaded loaded.") 
 # except: 
 #   response['error'].append("Gallery creation: "+str(e))
  
  #try:
  #  return render_template('gallery.html', links= gallery_images)
  #except Exception as e:
  #  response['error'].appen("Render Template failed. "+str(e))
 
  try:
    #target_file = url_for('static', filename="temp.jpg")
    target_file = "./static/temp.jpg"
    download_link = "https://pbs.twimg.com/media/FcTKvbdagAQ4sxk.jpg"
    res = requests.get(download_link, stream = True)
    if res.status_code == 200:  
      response['message'].append(res.status_code) 
      with open(target_file,'wb') as f:
          shutil.copyfileobj(res.raw, f) 
          response['message'].append("File downloaded") 
      f.close()
  except Exception as e: 
    response['error'].append(str(e)) 
  return response

@app.route('/single')
def dothis():
  birdname = request.args.get('birdname')
  imglink = request.args.get('img')
  bird_dict_comName = get_eBird_commonNames_data()
  speciesCode = search_speciesCode_by_commName(birdname,bird_dict_comName)
  eBird_link = "https://ebird.org/species/"+speciesCode
  if len(speciesCode)<2:  
    speciesCode, eBird_link = search_by_commonName_google(birdname)
   
  botw_link ="https://birdsoftheworld.org/bow/species/"+speciesCode+"/cur/introduction" 
  ##so now we have eBird link and birdoftheworld link
  
  try:
    soup = BeautifulSoup(return_html_code(eBird_link), 'html.parser')
    mat = soup.find_all("p", {"class": "u-stack-sm"})
    ebird_bird_description = mat[0].text
  except Exception as e: 
    ebird_bird_description = str(e)
  return render_template('single_bird.html', birdname=birdname, ebird_desc=ebird_bird_description, ebird_link= eBird_link,botw_link=botw_link, imglink=imglink )
  
  
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
    sent_ = request.args.get('sent')  #fetches the text via the argument. 
    response["messages"].append("user input recorded.")
      
    sent_ = basic_preprocess(sent_, spelling_corrections)   #preprocessing pipeline.
    response["messages"].append("user input processed.")
    
    for bird in all_birds:            #no chances of error here. 
      if sent_.find(bird) >-1:
        response["bird-wiki"].append(bird)  #if bird is found by rule matching from wikipedia link, it is appended.
    
    for bird_ in ebird_list:
      if sent_.find(bird_) >-1:
        response["bird-ebird"].append(bird_) #from the ebird list of birds.
       
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
