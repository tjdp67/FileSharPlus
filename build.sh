#!/bin/bash
docker stop filesharplus_app
docker rm fileshareplus_app
docker build -t fileshareplus .
docker run -d --name fileshareplus_app -p 8080:80 fileshareplus
