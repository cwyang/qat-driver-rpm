# -*- Mode: makefile-gmake -*-
# 1 September 2021
# Chul-Woong Yang

DOCKER=$(shell which docker 2> /dev/null)

KVER?=$(shell uname -r)
help:
	@echo "KVER=kernel_version make run"

docker:
	@[ -x "$(DOCKER)" ] || (echo "docker is not installed in this machine." && exit 1)
	docker build -f Dockerfile -t rpmbuild:latest .

run:
	docker run -it -v/usr/src:/usr/src -v/lib/modules:/lib/modules -v/tmp:/tmp -e"kver=${KVER}" rpmbuild:latest
