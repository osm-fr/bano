#!/bin/bash

set -e

for dep in {01..19} 2A 2B {21..95} {971..974}
do
	echo $dep
#	sh banout.sh $dep
done
