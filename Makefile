CLIENT_VER=0.0.1

export VAGRANT_DEFAULT_PROVIDER=libvirt
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

.vagrant/vfat.img:
	dd if=/dev/zero of=$@ bs=1024 count=10k
	printf 'n\np\n1\n\n\nt\nc\nw\n' | fdisk $@
	mformat -i$@@@1M -s32 -h64 -t9 -v"BNDRY TEST"
#.vagrant/vfat-windows.vdi: .vagrant/vfat.img
#	VBoxManage convertfromraw $< $@ --format vdi --uuid 00000000-4455-6677-8899-aabbccddeeff
.vagrant/vfat-macos.vdi: .vagrant/vfat.img
	VBoxManage convertfromraw $< $@ --format vdi --uuid 11111111-4455-6677-8899-aabbccddeeff

.PHONY: windows
windows:
	rm -rf windows
	$(VAGRANT) up windows
	tar cf - --xform 's,^,vagrant/,' `git ls-files` | \
	  $(VAGRANT) ssh windows --no-tty -c 'rm -rf /c/vagrant; tar xf - -C /c'
	$(VAGRANT) provision --provision-with build windows
	$(VAGRANT) ssh windows --no-tty -c 'tar cf - -C /c/vagrant windows' | tar xmf -
	$(VAGRANT) halt windows
.PHONY: windows-test
windows-test: windows/Boundery\ Client-$(CLIENT_VER).msi
	$(VAGRANT) up windows
	$(VAGRANT) provision --provision-with test windows
	$(VAGRANT) ssh windows --no-tty -c "[ -f /c/vagrant/windows/tests_passed ]"
	$(VAGRANT) halt windows
.PHONY: windows-gui
windows-gui:
	$(VAGRANT) rdp windows -- /cert-ignore +clipboard

.PHONY: macos
macos:
	rm -rf macOS
	$(VAGRANT) up macos
	$(VAGRANT) provision --provision-with build macos
	$(VAGRANT) ssh macos --no-tty -c "tar cf - -C /vagrant macOS" | tar xf -
	$(VAGRANT) halt macos
.PHONY: macos-test #XXX Make this depend on the built .dmg!
macos-test: .vagrant/vfat-macos.vdi
	rm -f macOS/tests_passed
	$(VAGRANT) up macos
	$(VAGRANT) provision --provision-with test macos
	$(VAGRANT) ssh macos --no-tty -c "[ -f /vagrant/macOS/tests_passed ]"
	$(VAGRANT) halt macos
.PHONY: macos-gui
macos-gui:
	vinagre localhost

.PHONY: dev
dev:
	@python3 -m boundery --debug --local

.PHONY: check
check:
	pyflakes3 `find boundery -name '*.py' | grep -v osal/__init__[.]py | grep -v osal/win32wifi[.]py`
