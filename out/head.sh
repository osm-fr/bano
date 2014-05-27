#!/bin/bash
for dep in {21..29}
do
	echo $dep
	sh banout.sh $dep
done
