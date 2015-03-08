#!/bin/bash
parallel -j 8 sh banout.sh > /dev/null -- 01 02 03 04 05 06 07 08 09 `seq 10 19` 2A 2B `seq 21 95` `seq 971 974`
