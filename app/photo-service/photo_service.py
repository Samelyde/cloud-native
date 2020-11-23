#!/usr/bin/env python3

import logging
import uvicorn
import json
from fastapi import Depends, FastAPI, HTTPException, File, UploadFile, Form
from starlette.requests import Request
from starlette.responses import Response
from photo import Photo
from mongoengine import *
from bson.objectid import ObjectId
from bson import json_util
from bson.errors import InvalidId
import pymongo
import json
import pprint
import base64
from io import BytesIO
from PIL import Image
import requests
from photo_const import Attribute, ATTRIBUTE_BODY, ATTRIBUTE_CREATION_BODY, Attributes
from photo_mongo_wrapper import *
from tags import TagsClient

tags_client = TagsClient()

mongo_service_host = 'mongo-service-photo'

mongo_service = mongo_service_host

# OK for testing or for running service
app = FastAPI(title = "Photo Service", debug = True)

@app.on_event("startup")
def startup_event():
    #connect("photo")
    connect("devops-f20-02-photo-db",
            username="devops-f20-02-user",
            password="DjNVhspvHhs4XTtb5N0P",
            host="mongo.cloud.rennes.enst-bretagne.fr")
    tags_client.connect("tags-service:80")

@app.post("/gallery/{display_name}", status_code = 201)
def post_photo(response: Response, display_name, file: UploadFile = File(...)):
    print('Post_Photo')
    try:
        
        r = requests.get('http://photographer-service/photographer/' + display_name)
        if r.status_code != 200:
            response.status_code = 404
            return 'Photographer not found', 404
        #photo_tags = tags_client.stub.getTags(tags_pb2.ImageRequest(file=file.file.read()))
        #ph = mongo_add(display_name, image=file, tags_photo=photo_tags)
        ph = mongo_add(display_name, image=file)
        response.headers['Location'] ='/photo/' + str(display_name) + '/' + str(ph.id)
        return {'path': response.headers['Location']}
    except (pymongo.errors.AutoReconnect,
            pymongo.errors.ServerSelectionTimeoutError,
            pymongo.errors.NetworkTimeout) as e:
        return 'Mongo unavailable', 503


@app.get("/gallery/{display_name}",status_code = 200)    
def get_photos(request:Request,display_name, offset: int = 0, limit: int = 10):
    print ("get photo")
    try:
        r = requests.get('http://photographer-service/photographer/' + display_name)
        if r.status_code != 200:
            return 'Photographer not found', 404
        json_array = []
        (has_more, list_of_photos) = mongo_get_photos(display_name, offset, limit)
        for ph in list_of_photos:
            json_data = {}
            json_data['link'] = request.headers['host'] + '/photo/' + str(display_name) + '/' + str(ph.id)
            json_array.append(json_data)
    except:
        return 'Not Found', 404
    return {'items': json_array, 'has_more': has_more}

    
@app.get("/photo/{display_name}/{photo_id}", status_code = 200)
def get_photo_by_id(display_name, photo_id):
    try:
        r = requests.get('http://photographer-service/photographer/' + display_name)
        if r.status_code != 200:
            return 'Photographer not found', 404

        ph = mongo_get_photo_by_id(display_name, photo_id)
        photo = ph.photo.read()
        return Response(content=photo, media_type="image/jpeg")
    except:
        return 'Not Found', 404

@app.delete("/photo/{display_name}/{photo_id}", status_code = 202)
def delete_photo_by_id(request: Request, display_name, photo_id):
    try:
        r = requests.get('http://photographer-service/photographer/' + display_name)
        if r.status_code != 200:
            return 'Photographer not found', 404

        r_photo = requests.get("http://" +request.headers['host']+ '/photo/' + str(display_name) + '/' + str(photo_id))
        if r_photo.status_code != 200:
            return 'Photo not found', 404

        ph = mongo_delete_photo_by_id(display_name, photo_id)
        print(str(ph))
        if ph:
            return 'NoContent', 202
        else:
            return 'Not Found', 404
    except (pymongo.errors.AutoReconnect,
            pymongo.errors.ServerSelectionTimeoutError,
            pymongo.errors.NetworkTimeout) as e:
        return 'Mongo unavailable', 503

@app.get("/photo/{display_name}/{photo_id}/attributes", status_code = 200)
def get_attributes_by_id(display_name, photo_id):
    try:
        r = requests.get('http://photographer-service/photographer/' + display_name)
        if r.status_code != 200:
            return 'Photographer not found', 404

        att = mongo_get_attributes_by_id(display_name, photo_id)
        return att, 200, {'Content-Type': 'application/json'}
    except:
        return 'Not Found', 404

@app.put("/photo/{display_name}/{photo_id}/attributes", status_code = 200)
def set_attributes_by_id(display_name, photo_id, attribute: Attribute = ATTRIBUTE_BODY):
    try:
        r = requests.get('http://photographer-service/photographer/' + display_name)
        if r.status_code != 200:
            return 'Photographer not found', 404
        photo = mongo_set_attributes_by_id(display_name, photo_id, attribute)
        return attribute, 201, {'Content-Type': 'application/json'}
    except Exception as exc:
        print("exception de type ", exc.__class__)
        # affiche exception de type  exceptions.ZeroDivisionError
        print("message", exc)
        # affiche le message associé à l'exception
        return 'Not Found', 404


if __name__ == "__main__":
    # if we run the main, the uvicorn.run() below will be executed
    # if we run the container from the docker image specifically made for
    #   fastAPI, there is no need to execute the main (uvicorn
    #   is run by the docker base image).
    uvicorn.run(app, host="0.0.0.0", port=8090, log_level="info")
