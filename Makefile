DOCKER=docker
VAGRANT=vagrant

.PHONY: linux
linux: DOCKER_EXTRA=$(shell [ -L build ] && P=$$(readlink build) && echo -v $$P/:$$P )
linux:
	$(DOCKER) build --build-arg UID=$$(id -u) --build-arg GID=$$(id -g) \
	  -t boundery-client-linux -f ./docker/Dockerfile.linux ./docker
	$(DOCKER) run -it --rm --user $$(id -u):$$(id -g) \
	  -v `pwd`/:/home/build/src $(DOCKER_EXTRA) boundery-client-linux \
	  python3 setup.py linux --build

#.PHONY: android
#android:
#	$(DOCKER) build --build-arg UID=$$(id -u) --build-arg GID=$$(id -g) \
#	  -t boundery-client-android -f ./docker/Dockerfile.android ./docker
#	$(DOCKER) run -it --rm --user $$(id -u):$$(id -g) \
#	  -v `pwd`/:/home/build/src $(DOCKER_EXTRA) boundery-client-android \
#	  /bin/sh -c "python3 setup.py android && python3 setup.py android --build"

.PHONY: windows
windows:
	rm -rf windows
	VAGRANT_VAGRANTFILE=Vagrantfile.windows $(VAGRANT) up
	VAGRANT_VAGRANTFILE=Vagrantfile.windows $(VAGRANT) provision --provision-with build
	while [ ! -f "windows/builddone" ]; do sleep 1; done
	VAGRANT_VAGRANTFILE=Vagrantfile.windows $(VAGRANT) halt
.PHONY: windows-gui
windows-gui:
	VAGRANT_VAGRANTFILE=Vagrantfile.windows vagrant rdp -- /cert-ignore
.PHONY: windows-halt
windows-halt:
	VAGRANT_VAGRANTFILE=Vagrantfile.windows vagrant halt
.PHONY: windows-destroy
windows-destroy:
	VAGRANT_VAGRANTFILE=Vagrantfile.windows vagrant destroy -f

.PHONY: dev
dev:
	@python3 boundery/app.py --debug --local

.PHONY: check
check:
	pyflakes3 `find boundery -name '*.py' | grep -v osal/__init__[.]py | grep -v osal/win32wifi[.]py`
