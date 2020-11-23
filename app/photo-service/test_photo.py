import pytest
from starlette.testclient import TestClient
import json
import logging

from photo_service import app

from fastapi import UploadFile
import base64,zlib, shutil
from io import BytesIO

from unittest.mock import Mock, patch
from tags import TagsClient
from photo_service import app, tags_client

#client = TestClient(app)
#tags_client.connect("tags-service:50051")

Data = {
    "title": "title1",
    "location": "location1",
    "comment": "comment2",
    "tags": ["tag2",],
    }

headers_content = {'Content-Type': 'multipart/form-data'}
headers_content1 = {'Content-Type': 'application/json'}
headers_accept  = {'Accept': 'application/json'}

client = TestClient(app)


@pytest.mark.usefixtures("clearPhotos")
@pytest.mark.usefixtures("initDB")
def test_post_once():
    with patch('photo_service.requests.get') as mock_get:
        # here, we force the Photographer service to return 200 OK.
        mock_get.return_value.status_code = 200
        image_file=BytesIO(base64.decodebytes(encoded_image))

        files = {'file': image_file}
        response = client.post('/gallery/joe', files=files)

        assert response.headers['Location']
        assert response.status_code == 201

@pytest.mark.usefixtures("clearPhotos")
@pytest.mark.usefixtures("initDB")
def test_post_once_with_unknown_photographer():
    with patch('photo_service.requests.get') as mock_get:
        # here, we force the Photographer service to return 404 Not Found.
        mock_get.return_value.status_code = 404
        image_file=BytesIO(base64.decodebytes(encoded_image))
        files = {'file': image_file}

        response = client.post('/gallery/joe', files=files)
        assert response.status_code == 404

@pytest.mark.usefixtures("clearPhotos")
@pytest.mark.usefixtures("initDB")
def test_get_all_photos():
    with patch('photo_service.requests.get') as mock_get:
        # here, we force the Photographer service to return 200 OK.
        mock_get.return_value.status_code = 200
        image_file=BytesIO(base64.decodebytes(encoded_image))
        files = {'file': image_file}

        response1 = client.post('/gallery/joe', files=files)

        assert response1.headers['Location']
        assert response1.status_code == 201

        response2 = client.get('/gallery/joe?offset=0&limit=10')
        
        assert response2.status_code == 200
        assert response2.json()['has_more'] == False

@pytest.mark.usefixtures("clearPhotos")
@pytest.mark.usefixtures("initDB")
def test_post_once_and_get_photo_by_id():
    with patch('photo_service.requests.get') as mock_get:
        # here, we force the Photographer service to return 200 OK.
        mock_get.return_value.status_code = 200
        image_file=BytesIO(base64.decodebytes(encoded_image))
        files = {'file': image_file}

        response1 = client.post('/gallery/joe', files=files)
        assert response1.headers['Location']
        assert response1.status_code == 201

        response2 = client.get('/gallery/joe?offset=0&limit=10')
        assert response2.status_code == 200
        assert response2.json()['has_more'] == False

        """link = response2.json()['items'][0]['link']        
        response3 = client.get(link)                
        assert link        
        assert response3.status_code == 200"""
        photoId = response2.json()['items'][0]['link'].split('/')[-1]
        response3 = client.get('/photo/joe/'+photoId)
        assert photoId
        assert response3.status_code == 200

@pytest.mark.usefixtures("clearPhotos")
@pytest.mark.usefixtures("initDB")
def test_delete_photo_by_id():
    with patch('photo_service.requests.get') as mock_get:
        # here, we force the Photographer service to return 200 OK.
        mock_get.return_value.status_code = 200
        image_file=BytesIO(base64.decodebytes(encoded_image))
        files = {'file': image_file}

        response1 = client.post('/gallery/joe', files=files)

        assert response1.headers['Location']
        assert response1.status_code == 201

        response2 = client.get('/gallery/joe?offset=0&limit=10')
        
        assert response2.status_code == 200
        assert response2.json()['has_more'] == False

        photoId = response2.json()['items'][0]['link'].split('/')[-1]
        response3 = client.get('/photo/joe/'+photoId)
        assert photoId
        assert response3.status_code == 200

        response4 = client.delete('/photo/joe/'+photoId)
        assert response4.status_code == 202


@pytest.mark.usefixtures("clearPhotos")
@pytest.mark.usefixtures("initDB")
def test_get_attributes_by_id():
    with patch('photo_service.requests.get') as mock_get:
        # here, we force the Photographer service to return 200 OK.
        mock_get.return_value.status_code = 200
        image_file=BytesIO(base64.decodebytes(encoded_image))
        files = {'file': image_file}

        response1 = client.post('/gallery/joe', files=files)

        assert response1.headers['Location']
        assert response1.status_code == 201

        response2 = client.get('/gallery/joe?offset=0&limit=10')
        
        assert response2.status_code == 200
        assert response2.json()['has_more'] == False

        photoId = response2.json()['items'][0]['link'].split('/')[-1]
        response3 = client.get('/photo/joe/'+photoId)
        assert photoId
        assert response3.status_code == 200

        response4 = client.get("/photo/joe/"+photoId+"/attributes")
        assert response4.status_code == 200

@pytest.mark.usefixtures("clearPhotos")
@pytest.mark.usefixtures("initDB")
def test_set_attributes_by_id():
    with patch('photo_service.requests.get') as mock_get:
        # here, we force the Photographer service to return 200 OK.
        mock_get.return_value.status_code = 200
        image_file=BytesIO(base64.decodebytes(encoded_image))
        files = {'file': image_file}

        response1 = client.post('/gallery/joe', files=files)

        assert response1.headers['Location']
        assert response1.status_code == 201

        response2 = client.get('/gallery/joe?offset=0&limit=10')
        
        assert response2.status_code == 200
        assert response2.json()['has_more'] == False

        photoId = response2.json()['items'][0]['link'].split('/')[-1]
        response3 = client.get('/photo/joe/'+photoId)
        assert photoId
        assert response3.status_code == 200

        response4 = client.put("/photo/joe/"+photoId+"/attributes",headers=headers_content1,
                           data=json.dumps(Data))
        assert response4.status_code == 200

encoded_image= b"""\
/9j/wAARCABaAIYDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QA
tRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkK
FhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJ
ipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx
8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcF
BAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygp
KjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJma
oqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9sA
QwAcHBwcHBwwHBwwRDAwMERcRERERFx0XFxcXFx0jHR0dHR0dIyMjIyMjIyMqKioqKioxMTExMTc
3Nzc3Nzc3Nzc/9sAQwEiJCQ4NDhgNDRg5pyAnObm5ubm5ubm5ubm5ubm5ubm5ubm5ubm5ubm5ubm
5ubm5ubm5ubm5ubm5ubm5ubm5ubm/90ABAAJ/9oADAMBAAIRAxEAPwDQBp4NQA08GkBODTwagBp4
NAEwNOqMGn0AOzUbAnpUlOAFO4GezEtinrCW5NXSiE5xzS4x0quYVikwKdaeobHtVgorHJFDA44p
XHYqFv71RhhjimsGJJalA7CrsRcecHjrUEhI4FWgh25HFR7FHLcmkmNoqbSaTY1WjTarmFyn/9Cy
DTwaiFOzQBMDTwagBp4NAFgGpAarqalBpATCpBUANSA0hktFMzS5oAWijNBNMCCWNTUexQOamY1C
TTuKwFqhY04mmGmhDDSUppKoD//Rl6UuacUHY0zY3Uc0KSCzHZpwNQnK9RigNTAshqkDVU3U8NSA
uBqlDVTUk1NntSsMm3U8NVfNPBp2Fcn3U0tUWaQmnysVxxNMJpCaTmq5bCuNNMJpSDSbGNIYlFBX
HWkwKYH/0hJFzxkVNlXPzfmKzMOOnNSLKy9axNDQVWXjORTWj7rVYTelTiZW9jTTaE0N5p4p6Df6
ZqcrtHJrZWZm9CNCakAPU0mQOKhkuY4uvJpXSHqX0TIzUwCjrWQNQP3QoqyL2Lblgc+lHMFi6wB6
UxdveqEl+NpCDH1qs1+VHqfejn6Bymu7Animqawf7QlZsYGPpUovJCcj8qHILG5lT1pDLEp2kge1
c7JdzyDAbb9KqjdnkmlcdjqjtbkYxSYHtXNFnYBSeB2pMNS5gsf/04PLPcUY9at4U8A807ZXPc1K
JRfSk2ejYq8Yz160wxL1IIouBWy6HrmpBPIRzQyDuQQPWosc/KfwpiA3EndSKrNIzHk1PuIbaRTs
buq5p3sIpHnvSByOM1e+zKRlePrUTWr/AMJFVzILFUsepNJnIqf7PMOw/Oo2hkX7wp3QhmQOlOGW
7mmbWzjFOwRQAp3A5pNz9DS4J7UgGPvYoAbyaMGlyoo3L6UAf//URQA3HNOaQLyetJMSqfLxVZOS
c81iol3JTOx6cVGZXPGakPCHFVl+8arlQrk23d8x/GgrjnrQvA/GkPUVBYzdxk07cQaa/wB0fWog
etVYkv8AmL0NN82LHBpjcKCPQ1VUdPx/lU2Hcu8NyDSEKR8wqqpO5fpVs96TQyExf3Dj69KjKN/E
v5VZNMzhqdwsVSOeDUZi9OfpWgwB61Ubg8U0ybFcp2pNlWTRVXCx/9k=
"""
