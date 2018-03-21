#!/bin/bash

COOKIE='cookie: __cfduid=decc881cda2134ffcc12749e71b09c4fe1519200097; ASP.NET_SessionId=jk2gttgxijowlohfrqjgpnix; uniqueuid=d459390d-83cc-46e7-81c1-35626985f2da; SESSf58986293761abff4873b1b3cc12d7de=8j3bjdkk9q5lmrut4n636mnes2; xf_user=99065%2C9225f748be455c08fb05ae74359cd4ead1edf5a9; xf_session=e2425a5c461c1cee601f241b33cff9e1; d_adb=1; d_viewed=; _ga=GA1.2.621192346.1519200099; _gid=GA1.2.360280027.1519713163'
USER_AGENT='user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'

depth=$1
table=$2
crown=$3
pavilion=$4

if [[ $# < 4 ]]; then
  echo "Usage: ./hca.sh depth table crown_angle pavilion_angle"
  exit 1
fi

hca_score=$(curl -s 'https://www.pricescope.com/tools/hca' \
  -H 'origin: https://www.pricescope.com' \
  -H "$COOKIE" \
  -H "$USER_AGENT" \
  -H 'content-type: application/x-www-form-urlencoded' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8' \
  -H 'referer: https://www.pricescope.com/tools/hca' \
  --data "gia_number=&size=&depth_textbox=$depth&table_textbox=$table&crown_textbox=$crown&pavilion_textbox=$pavilion&reffer_hca=" \
  | grep -o '<span id="newhca_rating">[0-9\.]*</span>' | sed 's/[^0-9\.]//g')

echo "$hca_score"
