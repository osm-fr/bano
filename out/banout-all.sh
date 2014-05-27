#!/bin/bash
for dep in {01..19} 2A 2B {30..95} {971..974}
do
	echo "Export du $dep"
	sh banout.sh $dep
done
