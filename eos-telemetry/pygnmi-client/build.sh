#!/bin/bash

#
# The script builds and run the pygnmi-client container
# If any changes to the Python code are needed (simplifies the process)
#

set -euo pipefail

IMAGE_NAME="bnet/pygnmi-client"
CONTAINER_NAME="pygnmi-client"
NETWORK_NAME="elastic"

# Stop the container if it exists
if docker container inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
    echo "Stopping and removing old container: $CONTAINER_NAME"
    docker container stop "$CONTAINER_NAME"
    sleep 2s
fi

# Remove the image if it exists
if docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
    echo "Removing old image: $IMAGE_NAME"
    docker image rm "$IMAGE_NAME"
    sleep 2s
fi

# Build the new image
echo "Building Docker image: $IMAGE_NAME"
docker build -t "$IMAGE_NAME" .

# Run the container
echo "Running container: $CONTAINER_NAME"
docker run --rm -d \
  --name "$CONTAINER_NAME" \
  --network "$NETWORK_NAME" \
  "$IMAGE_NAME"
