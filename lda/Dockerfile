FROM alpine:3.12

# python and dependecies
RUN apk add --update --no-cache \
	build-base linux-headers \ 
	python3 python3-dev py3-pip \
	libffi-dev zlib-dev libxml2 libxml2-dev libxslt-dev \
	openblas-dev lapack libstdc++ g++ gcc gfortran musl-dev lapack-dev

# php
RUN apk add --update --no-cache php7 php7-json curl

# add user
RUN addgroup -S user --gid 1000 && adduser -S user -G user --uid 1000 \
	&& mkdir -p /source/ \
	&& chown -R user:user /source/

# python lib
RUN pip3 install cython gensim scikit-learn

# change user/ path
WORKDIR /source/
USER user

# our code as python lib
ADD ./setup.py /source/setup.py
RUN pip3 install -e .