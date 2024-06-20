#!/bin/bash

set -e

source config
echo $EXPORT_SAS_DIR

DBLFILE=${EXPORT_SAS_DIR}/doublons.csv
rm -f ${DBLFILE}

for f in `ls ${EXPORT_SAS_DIR}/bano-*.csv`;
do
  # echo $f;
  b=`basename $f .csv`;
  shpcount=`ogrinfo -so ${EXPORT_SAS_DIR}/$b'.shp' $b|grep Count|awk '{print$3}'`
  csvcount=`wc -l $f|awk '{print $1}'`
  csvcountunique=`cat $f|sort -u|wc -l|awk '{print $1}'`
  diff <(sort ${f}) <(sort -u ${f}) >> ${DBLFILE}

  status_csv=`test ${csvcount} -eq ${csvcountunique} && echo ' '||echo 'x'`
  status_shp=`test ${csvcount} -eq ${shpcount} && echo ' '||echo 'x'`
  echo $b $csvcount $csvcountunique $shpcount $status_csv $status_shp #|awk 'BEGIN{print $1 $2 $3 $4 $5};FS=" ";OFS="\t"'
  #awk 'BEGIN{print $1 $2 $3 $4 $5};FS=" ";OFS="\t"' "$b $csvcount $csvcountunique $shpcount $status_csv $status_shp"
  # wc -l $f;
done