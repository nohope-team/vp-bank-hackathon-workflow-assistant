#!/bin/bash
set -x
set -e

VERSION_FILE_PATH="src/version.py"

if command -v docker-compose &> /dev/null; then
    build_command(){
        docker-compose build $1
    }
else
    build_command(){
        docker compose build $1
    }
fi

version=$(grep -oP '__version__ = "\K[0-9]+\.[0-9]+\.[0-9]+' "$VERSION_FILE_PATH")
if [[ -z "$version" ]]; then
    echo "Current version not found in $VERSION_FILE_PATH."
    exit 1
fi

echo --------- Build image  ---------

cd dockers
version=$version build_command $1
build_command $1

echo "Version $version built."
exit 0
