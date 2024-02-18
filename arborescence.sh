#!/bin/bash

set -e

source config
mkdir -p $LOG_DIR
mkdir -p $DATA_DIR
mkdir -p $BANO_CACHE_DIR
mkdir -p $BAN_CACHE_DIR
mkdir -p $CADASTRE_CACHE_DIR
mkdir -p $BAL_CACHE_DIR
mkdir -p $EXPIRE_TILES_DIR
mkdir -p $DOWNLOAD_DIR
mkdir -p $IMPOSM_CACHE_DIR
mkdir -p $COG_DIR
mkdir -p $EXPORT_SAS_DIR
mkdir -p $EXPORT_WEB_DIR
mkdir -p $TMP_DIR