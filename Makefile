DOCKER=docker

.PHONY: linux
#linux: DOCKER_EXTRA=$(shell [ -L build ] && P=$$(readlink build) && echo -v $$P/:$$P )
linux:
	$(DOCKER) build --build-arg UID=$$(id -u) --build-arg GID=$$(id -g) \
	  -t boundery-client-linux -f ./docker/Dockerfile.linux ./docker
	$(DOCKER) run -it --rm --user $$(id -u):$$(id -g) \
	  -v `pwd`/:/home/build/src $(DOCKER_EXTRA) boundery-client-linux \
	  python3 setup.py linux

.PHONY: android
android:
	$(DOCKER) build --build-arg UID=$$(id -u) --build-arg GID=$$(id -g) \
	  -t boundery-client-android -f ./docker/Dockerfile.android ./docker
	$(DOCKER) run -it --rm --user $$(id -u):$$(id -g) \
	  -v `pwd`/:/home/build/src $(DOCKER_EXTRA) boundery-client-android \
	  /bin/sh -c "python3 setup.py android && python3 setup.py android --build"

