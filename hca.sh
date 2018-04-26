#!/bin/bash

COOKIE='cookie: __cfduid=de8ffcd3e94941478dddf9674058388381524722249; ASP.NET_SessionId=qrbiiezdcv30padytciszety; uniqueuid=46b00de6-bea7-4cb2-b5df-4e4b4b462f06; _ga=GA1.2.1592893582.1524722251; _gid=GA1.2.1861870099.1524722251; __gads=ID=b13d85dd2af3d136:T=1524722251:S=ALNI_MYI2ECsQWdkIzNdUh7kqfpFoiLv5g; d_adb=1; xf_user=101362%2C9886ed932cc477ab76c8e1783139345b36689bfd; xf_session=4dc959b67150f78a56fe39a5ab662ecd; d_viewed='
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
  -H 'authority: www.pricescope.com' \
  -H 'cache-control: max-age=0' \
  -H 'origin: https://www.pricescope.com' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H "$COOKIE" \
  -H "$USER_AGENT" \
  -H 'content-type: application/x-www-form-urlencoded' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8' \
  -H 'referer: https://www.pricescope.com/tools/hca' \
  --data "gia_number=&size=&depth_textbox=$depth&table_textbox=$table&crown_textbox=$crown&pavilion_textbox=$pavilion&reffer_hca=" \
  | grep 'Total Visual Performance' | grep -oi '<font.*font>' | sed 's/<[^>]*>//g;s/&nbsp;/ - /g')

echo "$hca_score"
