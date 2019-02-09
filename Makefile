DOCKER=docker

.PHONY: linux
#dockerbuild: DOCKER_EXTRA=$(shell [ -L build ] && P=$$(readlink build) && echo -v $$P/:$$P )
dockerbuild:
	$(DOCKER) build --build-arg UID=$$(id -u) --build-arg GID=$$(id -g) \
	  -t boundery-client -f ./docker/Dockerfile.linux ./docker
	$(DOCKER) run -it --rm --user $$(id -u):$$(id -g) \
	  -v `pwd`/:/home/build $(DOCKER_EXTRA) boundery-client \
	  python3 setup.py linux

