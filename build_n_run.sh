#!/usr/bin/env bash

set -e

docker image build -t shil:latest .
docker container run -it --rm shil
