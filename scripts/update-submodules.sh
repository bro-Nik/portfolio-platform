#!/bin/bash

echo "Updating all submodules..."
git submodule update --remote --recursive

echo "Status of submodules:"
git submodule status
