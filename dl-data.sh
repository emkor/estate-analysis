#!/usr/bin/env bash

set -e

BUCKET_DIR=$1
DATA_DIR=$2

mkdir -p "$BUCKET_DIR"
b2 authorize-account "${B2_KEY_ID}" "${B2_APP_KEY}"
BUCKET_FILES=$(b2 ls "${B2_BUCKET}")
BUCKET_FILES_COUNT=$(echo "$BUCKET_FILES" | wc -l)
LOCAL_FILES=$(for f in $(find "$BUCKET_DIR" -type f -name "*.csv.zip"); do basename "$f"; done)
TO_DOWNLOAD=$(echo "$BUCKET_FILES" | grep -v "$LOCAL_FILES" | sort | uniq)
TO_DOWNLOAD_COUNT=$(echo "$TO_DOWNLOAD" | wc -l)

echo "Downloading $TO_DOWNLOAD_COUNT out of $BUCKET_FILES_COUNT available in bucket into $BUCKET_DIR..."
for file in $TO_DOWNLOAD; do b2 download-file-by-name --noProgress "$B2_BUCKET" "$file" "$BUCKET_DIR/$file"; done

TO_UNPACK=$(find "$BUCKET_DIR" -type f -name "*.csv.zip")
TO_UNPACK_COUNT=$(echo TO_UNPACK_COUNT | wc -l)
echo "Unpacking $TO_UNPACK_COUNT files from $BUCKET_DIR into $DATA_DIR..."
mkdir -p "$DATA_DIR"
for file in $TO_UNPACK; do unzip -n -d "$DATA_DIR" "$file"; done
echo "Done"
