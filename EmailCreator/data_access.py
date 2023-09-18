from urllib.request import Request,urlopen
import urllib.request
import bs4 as bs
from bs4 import BeautifulSoup
from langchain.document_loaders import UnstructuredURLLoader
import pandas as pd
import openai
import re
import time
import os
import numpy as np
from langchain.vectorstores import Qdrant
import qdrant_client
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct
from error_handling import error_map
#from dotenv import load_dotenv
#from flask import Flask, request, jsonify
from flask import jsonify
from dotenv import load_dotenv

load_dotenv()


##openai.api_key =
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_APIKEY =os.getenv("QDRANT_APIKEY")

def web_scrapping(sample_website):
    try:
        #sample_website=input("Please enter your url : ")
        Requested_page = Request(sample_website)
        try:
            page = urlopen(Requested_page)
        except:
            return({"statusCode": 500,
                    "statusMessage": "Uploded URL is incorrect. Please upload correct one"
                    })
        soup = bs.BeautifulSoup(page,"lxml")
        links = []
        j=0
        for link in soup.findAll("a"):
            if ("http" in link['href']):
                links.append(link.get('href'))
            if(j==5):
                break
            j+=1
        loader = UnstructuredURLLoader(urls=links)
        data = loader.load()
        return {"statusCode": 200,
                "statusMessage": "Uploded URL is correct.",
                "dataAttached":{"scrappedData":data
                               }
                }
    except Exception as e:
        return error_map(e)

def data_cleaning(data):
    try:
        link = [info.metadata for info in data]
        records = [info.page_content for info in data]  # will add 2 rows, one for url, 2nd one for content
        remove_nc = [nc.replace("\n", " ") for nc in records] #remove new line
        remove_tab = [rt.replace("\t"," ") for rt in remove_nc] #remove tab
        final_data = [re.sub(' +', ' ', string) for string in remove_tab] #remove extra space
        fileExistance = file_exist()
        if fileExistance["statusCode"] == 500:          
            index = [num for num in range(1,len(records)+1)]
        else:
            directory = os.getcwd()
            indexDf = pd.read_csv(directory+"\index.csv")
            previousIndex = list(indexDf["index"])
            index = [num for num in range(previousIndex[-1]+1,previousIndex[-1]+len(records)+1)]
        dataframe = {"index":index,"URL":link,"Content":final_data} #dataframe create
        df = pd.DataFrame(dataframe)
        #print("df index are: ",df["index"])
        df.to_csv("index.csv",index=False)
        return df
    except Exception as e:
        return error_map(e)

def file_exist():
    try:
        directory = os.getcwd()
        index_file = pd.read_csv(directory+"\index.csv")
        return {"statusMessage":"File exist",
                "statusCode":200
            }
    except:
        return {"statusMessage":"File not exist",
                "statusCode":500
            }
    
def qdrant_create():
    try:
        client = qdrant_client.QdrantClient(QDRANT_HOST,api_key=QDRANT_APIKEY,timeout=300000)
        vector_config = qdrant_client.http.models.VectorParams(size=1536,# the dimension that is used by model example openai embedding use 1536 and instructor uses 786  
                    distance=qdrant_client.http.models.Distance.COSINE) #it will use cosine similarity search
        try :
            cont = client.get_collection(collection_name="email_creator")
            print("vector store already exist")
        except:
            client.recreate_collection(
            collection_name="email_creator", 
            vectors_config=vector_config)
            print("vector store is created")
        return client
    except Exception as e:
        return error_map(e)

def create_embeddings(df):
    try:
        dfList = []
        for index, row in df.iterrows():
            print(index)
            entry = {}
            entry['index'] = row['index']
            entry['URL'] = row['URL']
            entry['Content'] = row['Content']
            if len(row['Content']) <33000:
                # ... set the 'embedding' key in the dictionary to the result of calling the 'openai.Embedding.create' function on the 'Content' value
                entry['embedding'] = openai.Embedding.create(
                    input = row['Content'], model="text-embedding-ada-002")['data'][0]['embedding']
                print("delay of 30 sec, please wait for embedding ")
                time.sleep(30)
            else:
                # ... split the 'Content' value at the first period (.) after the middle of the string and take the second half as the first substring
                embedding1 = openai.Embedding.create(
                    input = row['Content'][row['Content'].find('.', int (len(row['Content'])/2))+1:], model="text-embedding-ada-002")['data'][0]['embedding']
                print("delay of 20 sec, please wait for embedding 1")
                time.sleep(20)
                # ... take the first half of the 'Content' value as the second substring
                embedding2 = openai.Embedding.create(
                    input = row['Content'][:row['Content'].find('.', int (len(row['Content'])/2))+1], model="text-embedding-ada-002")['data'][0]['embedding']
                print("delay of 20 sec, please wait for embedding 2")
                time.sleep(20)
                # ... set the 'embedding' key in the dictionary to the mean of the embeddings of the two substrings
                entry['embedding'] = np.mean([embedding1, embedding2], axis=0)
            # Add the dictionary to the list
            dfList.append(entry)
        #=======final dataframe
        # Convert the list of dictionaries into a new dataframe and store it in the 'df' variable, overwriting the original dataframe
        df_embed = pd.DataFrame(dfList)
        return df_embed
    except Exception as e:
        return error_map(e)

def store_database(df,userinput):
    try:
        client = qdrant_create()
        #payload = df.drop(['index', 'URL','embedding'], axis=1).to_dict(orient="records")
        #==== upload data in qdrant database
        for id_num,vector_num in zip(list(df["index"]),list(df['embedding'])):
            client.upsert(
                collection_name="email_creator",
                points=[PointStruct(
                    id = id_num,
                    vector=vector_num,
                    payload={
                        'Content': userinput
                    })
                    ])
            return {"statusCode": 200,
                     "statusMessage": "Embedding stored in cloud successfully."
                    }
    except Exception as e:
        return error_map(e)

def process_website(website,index_name):
    try:
        websiteData = web_scrapping(website)
        if websiteData["statusCode"]==200:
            print("websiteData  got")
            data = websiteData["dataAttached"]["scrappedData"]
        else:
            print("eroor")
            return {"statusCode":websiteData["statusCode"],
                    "statusMessage":websiteData["statusMessage"],
                    "dataAttached": None}
        df = data_cleaning(data)  # create dataframe
        #print("df ", df)
        df_embedding = create_embeddings(df)   #embedding created
        
        database = store_database(df_embedding,index_name) #upload embeddings in db
        if database["statusCode"] == 200:
            print("database done")
            return {"statusCode": 200, "statusMessage": 'Proccess completed successfully'}
        else:
            print("error")
            return {"statusCode": 500,
                    "statusMessage":"Error Occurred: "  + str(database["statusMessage"])
                    }
    except Exception as e:
        return error_map(e)
