#!/bin/bash

for i in $*; do
  echo -n "Checking $i... "
  wget -q https://yadav-videos.s3.amazonaws.com/$i.mp4
  mp4=$?
  wget -q https://yadav-certs.s3.amazonaws.com/$i.pdf
  pdf=$?
  wget -q https://yadav-certs.s3.amazonaws.com/$i.jpg
  jpg=$?
  if [[ $mp4 -eq 0 || $pdf -eq 0 || $jpg -eq 0 ]]; then
    echo "Successful"
  else
    echo "Failed"
  fi
done
