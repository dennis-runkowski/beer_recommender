#!/bin/bash

set -e

echo "###############################"
echo "Building beer_recommender package...."
echo "###############################"

timestamp=$(date +%s)

tar --exclude='../../beer_recommender/deployment/packages' --exclude='beer_recommender/.git' -czvf packages/build_$timestamp.tar.gz ../../beer_recommender

echo ""
echo "#######################################"
echo "Completed"
echo "Package Name: build_$timestamp.tar.gz"
echo "#######################################"