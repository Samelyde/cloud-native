#!/usr/bin/env python3

import logging
import json
import uvicorn

from fastapi import Path, Body
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from starlette.responses import Response, StreamingResponse
from starlette.requests import Request
import re

from backend_const import Dname, Photographer, PHOTOGRAPHER_BODY, Photographers, PhotoAttributes, PHOTO_ATTRIBUTES_BODY

from bson.objectid import ObjectId
from bson import json_util
from bson.errors import InvalidId

import json

import requests
from urllib.parse import urlparse

from backend_const import REQUEST_TIMEOUT
from starlette.middleware.cors import CORSMiddleware

photo_service = 'http://photo-service/'
photographer_service = 'http://photographer-service/'


app = FastAPI(title="Backend Service", debug = True)

# origins = [
#     "http://localhost",
#     "http://localhost:8080",
#     "http://localhost:3000",
#     "localhost:3000",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


@app.get("/gallery/{display_name}", status_code=200)
def get_photos(request: Request, display_name: str = Dname.PATH_PARAM, offset: int = 0, limit: int = 10):
    try:
        photos = requests.get(photo_service + "gallery/" + display_name +
                              '?offset=' + str(offset) +
                              '&limit=' + str(limit),
                              timeout=REQUEST_TIMEOUT)
        if photos.status_code == requests.codes.ok:
            # adapt the results to the backend API
            photos_dict = photos.json()
            try:
                lien = []
                for p in photos_dict['items']:
                    lien1= urlparse(p['link']).path.replace('photo-service/','')
                    lien.append(lien1)
                return ["http://" + request.headers['host'] +"/" + lien[p]
                        for p in range(0,len(lien))]
            except (KeyError, TypeError) as e:
                # Hack to support photo service implementation that does not return
                # expected json {
                #   "items": [
                #    {
                #      "photo_id": 1,
                #      "link": "http://localhost:8080/photo/rdoisneau/1"
                #    }],
                #  "has_more": false }
                return ["http://" + request.headers['host'] +"/"+urlparse(p).path
                        for p in photos_dict]
    
        elif photos.status_code == requests.codes.not_found:
            raise HTTPException(status_code=404, detail="Not Found")
        elif photos.status_code == requests.codes.unavailable:
            raise HTTPException(status_code=503, detail="Service Unavailable")
        else:
            photos.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail="Service Unavailable")


@app.post("/gallery/{display_name}", status_code=201)
def upload_photo(response: Response,
                 request: Request,
                 display_name: str = Dname.PATH_PARAM,
                 upfile: UploadFile = File(...)):
    try:
        files = {'file': upfile.file}
        r = requests.post(photo_service + "gallery/" + display_name,
                          files=files,
                          timeout=REQUEST_TIMEOUT)
        if r.status_code == requests.codes.created:
            location = urlparse(r.headers['location'])
            response.headers["location"] = "http://" + \
                request.headers['host'] + "/"+location.path
        elif r.status_code == requests.codes.not_found:
            raise HTTPException(status_code=404, detail="Not Found")
        elif r.status_code == requests.codes.unavailable:
            raise HTTPException(status_code=503, detail="Service Unavailable")
        else:
            r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail="Service Unavailable")


@app.put("/photo/{display_name}/{photo_id}/attributes", status_code=200)
def set_photo_attributes(display_name: str = Dname.PATH_PARAM,
                         photo_id: str = Path(..., title="Id of the photo", example=1),
                         attributes: PhotoAttributes = PHOTO_ATTRIBUTES_BODY):
    try:
        r = requests.put(photo_service + "photo/" + display_name + "/" + str(photo_id) + "/attributes",
                         json=vars(attributes),
                         timeout=REQUEST_TIMEOUT)
        if r.status_code == requests.codes.ok:
            return
        elif r.status_code == requests.codes.not_found:
            raise HTTPException(status_code=404, detail="Not Found")
        elif r.status_code == requests.codes.unavailable:
            print('here')
            raise HTTPException(status_code=503, detail="Service Unavailable")
        else:
            r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        raise HTTPException(status_code=503, detail="Service Unavailable")

@app.get("/photo/{display_name}/{photo_id}/attributes",
         response_model=PhotoAttributes, status_code=200)
def get_photo_attributes(display_name: str = Dname.PATH_PARAM,
                         photo_id: str = Path(...,
                                              title="Id of the photo", example=1)
                         ):
    try:
        r = requests.get(photo_service + "photo/" + display_name + "/" + str(photo_id) + "/attributes",
                         timeout=REQUEST_TIMEOUT)
        if r.status_code == requests.codes.ok:
            return r.json()
        elif r.status_code == requests.codes.not_found:
            raise HTTPException(status_code=404, detail="Not Found")
        elif r.status_code == requests.codes.unavailable:
            raise HTTPException(status_code=503, detail="Service Unavailable")
        else:
            r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail="Service Unavailable")


@app.get("/photo/{display_name}/{photo_id}", status_code=200)
def get_photo(display_name: str, photo_id: str):
    try:
        r = requests.get(photo_service + "photo/" + display_name + "/" + str(photo_id),
                         timeout=REQUEST_TIMEOUT)
        if r.status_code == requests.codes.ok:
            return Response(content=r.content, media_type="image/jpeg")
        elif r.status_code == requests.codes.not_found:
            raise HTTPException(status_code=404, detail="Not Found")
        elif r.status_code == requests.codes.unavailable:
            raise HTTPException(status_code=503, detail="Service Unavailable")
        else:
            r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail="Service Unavailable")


@app.get("/photographers", status_code=200)
def get_photographers(request: Request, offset: int = 0, limit: int = 10):
    try:
        photographers = requests.get(photographer_service + "photographers" +
                                     '?offset=' + str(offset) +
                                     '&limit=' + str(limit),
                                     timeout=REQUEST_TIMEOUT)
        if photographers.status_code == requests.codes.ok:
            has_more = photographers.json()['has_more']
            list_of_photographers = list()
            for p in photographers.json()['items']:
                pp = {
                    'link': "http://" + request.headers['host'] + urlparse(p['link']).path,
                    'display_name': p['display_name']
                }
                list_of_photographers.append(pp)
            return {'items': list_of_photographers, 'has_more': has_more}
        elif photographers.status_code == requests.codes.not_found:
            raise HTTPException(status_code=404, detail="Not Found")
        elif photographers.status_code == requests.codes.unavailable:
            raise HTTPException(status_code=503, detail="Service Unavailable")
        else:
            photographers.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail="Service Unavailable")

@app.get("/photographer/{display_name}", response_model=Photographer, status_code=200)
def get_photographer(display_name: str = Dname.PATH_PARAM):
    try:
        r = requests.get(photographer_service + "photographer/" + display_name,
                         timeout=REQUEST_TIMEOUT)
        if r.status_code == requests.codes.ok:
            return r.json()
        elif r.status_code == requests.codes.not_found:
            raise HTTPException(status_code=404, detail="Not Found")
        elif r.status_code == requests.codes.unavailable:
            raise HTTPException(status_code=503, detail="Service Unavailable")
        else:
            r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail="Service Unavailable")


@app.post("/photographers", status_code=201)
def post_photographers(response: Response,
                       request: Request,
                       photographer: Photographer = PHOTOGRAPHER_BODY):
    try:
        r = requests.post(photographer_service + "photographers",
                          json=vars(photographer),
                          timeout=REQUEST_TIMEOUT)
        if r.status_code == requests.codes.created:
            location = urlparse(r.headers['location'])
            response.headers["location"] = "http://" + \
                request.headers['host'] + location.path
        elif r.status_code == requests.codes.not_found:
            raise HTTPException(status_code=404, detail="Not Found")
        elif r.status_code == requests.codes.unavailable:
            raise HTTPException(status_code=503, detail="Service Unavailable")
        elif r.status_code == requests.codes.conflict:
            raise HTTPException(status_code=409, detail="Conflict")
        else:
            r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail="Service Unavailable")


if __name__ == "__main__":
    # Seems that a default alias is necessary ... so use default for photos ...
    uvicorn.run(app, host="0.0.0.0", log_level="debug")
