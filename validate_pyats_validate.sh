#!/bin/bash

if [ -s "./test_results.txt" ]; then
	echo file size greater than 0
	cat "./test_results.txt"
	exit 1
else
	echo file size is 0
	exit 0
fi
