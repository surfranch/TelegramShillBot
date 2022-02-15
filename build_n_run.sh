#!/usr/bin/env bash

set -e

function usage {
    echo """
Usage:
  build_n_run.sh [OPTIONS]

Options:
  -n STRING     Name the image and running container
  -h            Show help message
"""
}

NAME="shillbot"

while getopts ":n:h" opt; do
  case ${opt} in
  n)
    if [[ $OPTARG =~ ^[a-zA-Z0-9]+$ ]]; then
      NAME=$OPTARG
    else
      echo "Invalid container name ($OPTARG), only [a-zA-Z0-9] is allowed."
      usage
      exit 1
    fi
    ;;
  h)
    usage
    exit 1
    ;;
  ?)
    echo "Invalid option: -$OPTARG" 1>&2
    usage
    exit 1
    ;;
  esac
done

docker image build -t ${NAME}:latest .
docker container run --name ${NAME} -it --rm ${NAME}
