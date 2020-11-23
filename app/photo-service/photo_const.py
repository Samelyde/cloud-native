#!/usr/bin/env python3

from fastapi import Path, Body
from pydantic import BaseModel, Field
from typing import List

class Title:
    STR = "The title of the photo"
    MAX_LENGTH = 16
    PATH_PARAM = Path(..., title = STR, max_length = MAX_LENGTH)

class Location:
    STR = "The location of the photo"
    MAX_LENGTH = 32

class Aname:
    STR = "The name of the author corresponding to the name the photographer"
    MAX_LENGTH = 32
    
class Comment:
    STR = "Comment about photo"
    MAX_LENGTH = 120
class Tags:
    STR = "List of tags"

class Attribute(BaseModel):
    title: str = Field (None, title = Title.STR, max_length = Title.MAX_LENGTH)
    location: str = Field (None, title = Location.STR, max_length = Location.MAX_LENGTH)
    author: str = Field (None, title = Aname.STR, max_length = Aname.MAX_LENGTH)
    comment: str = Field (None, title = Comment.STR, max_length = Comment.MAX_LENGTH)
    tags: List[str] = Field (None, title = Tags.STR)

ATTRIBUTE_EXAMPLE = {
    "title": "title",
    "location": "location",
    "comment": "comment",
    "tags": ["tags",],
    }

ATTRIBUTE_CREATION_EXAMPLE = {
    "title": "",
    "location": "",
    "author": "",
    "comment": "",
    "tags": [],
    }

ATTRIBUTE_BODY = Body(..., example = ATTRIBUTE_EXAMPLE)
ATTRIBUTE_CREATION_BODY = Body(..., example = ATTRIBUTE_CREATION_EXAMPLE)

class AttributeDigest(BaseModel):
    author: str
    
    link: str

class Attributes(BaseModel):
    items: List[AttributeDigest]
    has_more: bool
