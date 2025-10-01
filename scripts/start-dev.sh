#!/bin/bash

echo "Pulling latest changes from submodules..."
git submodule update --init --recursive
git submodule update --remote

echo "Starting development environment..."
docker-compose up -d --build

echo "Services are starting..."
