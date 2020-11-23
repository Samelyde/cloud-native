#!/usr/bin/env python3

from fastapi import Path, Body
from pydantic import BaseModel, Schema
from typing import List

REQUEST_TIMEOUT = 5

# OK, this is copy/paste from photographer_const but the backend_service
# given to student must be self-contained.

class Dname:
    STR = "The display name of the photographer"
    MAX_LENGTH = 16
    # does it make sense to define it as a class attribute ?
    PATH_PARAM = Path(..., title = STR, max_length = MAX_LENGTH, example = "rdoisneau")

class Fname:
    STR = "The first name of the photographer"
    MAX_LENGTH = 32

class Lname:
    STR = "The last name of the photographer"
    MAX_LENGTH = 32

class Interests:
    STR = "The interests of the photographer"

class Photographer(BaseModel):
    display_name: str = Schema (None, title = Dname.STR, max_length = Dname.MAX_LENGTH)
    first_name: str = Schema (None, title = Fname.STR, max_length = Dname.MAX_LENGTH)
    last_name: str = Schema (None, title = Lname.STR, max_length = Lname.MAX_LENGTH)
    interests: List[str] = Schema (None, title = Interests.STR)

PHOTOGRAPHER_EXAMPLE = {
    "display_name": "rdoisneau",
    "first_name": "robert",
    "last_name": "doisneau",
    "interests": ["street", "portrait"],
    }

PHOTOGRAPHER_BODY = Body(..., example = PHOTOGRAPHER_EXAMPLE)

class PhotographerDigest(BaseModel):
    display_name: str
    link: str

class Photographers(BaseModel):
    items: List[PhotographerDigest]
    has_more: bool

class PhotoAttributes(BaseModel):
    title: str
    comment: str
    location: str
    author: str
    tags: List[str]

PHOTO_ATTRIBUTES_EXAMPLE = {
    "title": "Sunset",
    "comment": "Sunset in Summer",
    "location": "Morbihan",
    "author": "joe",
    "tags": ["sunset", "summer", "bretagne"],
}

PHOTO_ATTRIBUTES_BODY = Body(..., example = PHOTO_ATTRIBUTES_EXAMPLE)


class PhotoDigest(BaseModel):
    photo_id: int
    link: str

class Photos(BaseModel):
    items: List[PhotoDigest]
    has_more: bool
