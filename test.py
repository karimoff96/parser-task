import requests
from bs4 import BeautifulSoup
import datetime
import collections
import csv
import json


def datetime_now():
    '''Method of defining current datetime'''
    return datetime.datetime.now().astimezone().strftime('%Y.%m.%d %H:%M:%S')

# Step1. Bronze layer. Data acquisition

def parsing_data(URL = "https://kun.uz/uz"):
    r = requests.get(url=URL)
    soup = BeautifulSoup(r.content, 'html5lib')
    lentas = soup.find('div', attrs = {'class':'mb-25'}) 
    datas=[]
    for lenta in lentas.findAll('a', attrs={'class': 'news-lenta'}):
        data={}
        data['title'] = lenta.find('span', attrs ={'class': 'news-lenta__title'}).text
        data['source_url'] = lenta['href']

        new_url = URL+ lenta['href'][3:]
        r = requests.get(url=new_url)
        soup1 = BeautifulSoup(r.content, 'html5lib')
        single_content=soup1.find('div', attrs={'class':'single-content'})
        
        data['access_datetime']=datetime_now()
        texts = [text.text for text in single_content.findAll('p')]
        data['content']=' '.join(texts)

        # Step 2. Silver layer. Basic transformations
        data['words']=' '.join(texts).split()

        # Step 3. Let’s gather some stats!
        elements_count = collections.Counter(' '.join(texts).split())
        words = []
        for key, value in elements_count.items():
            words.append(f"{key}: {value}")
        data['word_frequency']=words
        datas.append(data)
        return datas

# saving data into JSON file
def get_json(filename: str):
    '''Accepts filename and returns the collected data as json file'''
    for data in parsing_data():
        dictionary = {
            'Title': data["title"],
            'Source URL': data["source_url"],
            'Access Datetime': data["access_datetime"],
            'Content': data["content"],
            'Words': data["words"],
            'Word Frequency': data["word_frequency"]            
        }
    # Serializing json
    json_object = json.dumps(dictionary, indent=4)

    # Writing to sample.json
    with open(filename+".json", "w") as outfile:
        outfile.write(json_object)


# Saving all data into CSV file
def get_csv(filename: str):
    '''Accepts filename and returns the collected data as csv file'''

    csv_columns = list([title.keys() for title in parsing_data()][0])
    dict_data = [data for data in parsing_data()]
    try:
        with open(filename+'.csv', 'w', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except IOError:
        return "I/O error"

get_json('dataset')
get_csv('file')
