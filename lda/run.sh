#!/bin/sh
if [ $# = "1" ]; then
	if [ $1 = "b" ]; then
		docker-compose build lda
	fi;
fi;

docker-compose run lda