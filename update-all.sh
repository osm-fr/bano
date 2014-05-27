#!/bin/bash
for dep in {01..19} 2A 2B {21..95} {971..974}
do
	python load_cumul.py $dep CADASTRE
	python load_cumul.py $dep OSM
	pushd out/
	sh banout.sh $dep
	popd
done
