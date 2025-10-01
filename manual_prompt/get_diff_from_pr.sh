#!/bin/bash

set -e
ROOT_FOLDER=$(dirname $0)

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
BASE_BRANCH=${1:-origin/main}
TARGET_BRANCH=${2:-$CURRENT_BRANCH}

# get the diff between the two branches
git diff $BASE_BRANCH $TARGET_BRANCH >$ROOT_FOLDER/diff.txt

echo "Diff between $BASE_BRANCH and $TARGET_BRANCH saved to $ROOT_FOLDER/diff.txt"

if [ $? -ne 0 ]; then
    echo "Failed to get the diff between $BASE_BRANCH and $TARGET_BRANCH."
    exit 1
fi

if [ ! -s $ROOT_FOLDER/diff.txt ]; then
    echo "No changes found between $BASE_BRANCH and $TARGET_BRANCH."
    exit 0
fi
