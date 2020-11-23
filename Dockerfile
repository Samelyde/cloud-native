<<<<<<< HEAD
FROM python:3
ADD file1.html data/
ADD file2.html data/
ADD file3.html data/
=======
FROM ws:latest
<<<<<<< HEAD
WORKDIR /data
ADD file1.html /data
ADD file2.html /data
ADD file3.html /data
EXPOSE 8080
CMD ["python3","-m","http.server","8080"]
=======
ADD file1.html data/
ADD file2.html data/
ADD file3.html data/
EXPOSE 8080
>>>>>>> 89f78946facd2f415b6b32d92f7572aabec37d1f
WORKDIR /data
CMD ["python3","-m","http.server","8080"]









<<<<<<< HEAD
=======
>>>>>>> f8321cfc5f45ebf01cce8b573c14fbeed930db94
>>>>>>> 89f78946facd2f415b6b32d92f7572aabec37d1f
