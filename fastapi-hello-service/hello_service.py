#!/usr/bin/env python3

import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi import Path

app = FastAPI()

@app.get("/hello", status_code=200)
def say_hello():
    return {'message': 'hello'}


@app.get("/hello/{firstname}", status_code=200)
def response (firstname : str, level: str ):
    if level=='familiar':
        return {'message': f'hello {firstname}'}
    elif level=='formal':
        return {'message': f'Nice to meet you {firstname}'}    
    else :
        return {'message': f'Greetings {firstname}'}
    


if __name__ == "__main__":
    uvicorn.run(app, log_level="info")

