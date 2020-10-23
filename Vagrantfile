raise "Run: vagrant plugin install winrm" unless Vagrant.has_plugin?('winrm')
raise "Run: vagrant plugin install winrm-elevated" unless Vagrant.has_plugin?('winrm-elevated')

def add_usb_vdi(vb, machine)
  vdi = File.join(File.dirname(File.expand_path(__FILE__)), ".vagrant/vfat-#{machine}.vdi")
  if not File.exist?(vdi)
    return
  end
  id = File.read(".vagrant/machines/#{machine}/virtualbox/id")
  if `VBoxManage showvminfo #{id} --machinereadable | egrep '^storagecontrollername[0-9]+="BOUNDERYUSB"$'`.length <= 0
    vb.customize ['storagectl', id, '--name', 'BOUNDERYUSB', '--add', 'usb', '--controller', 'USB']
  end
  vb.customize ['storageattach', id, '--storagectl', 'BOUNDERYUSB',
                '--port', 1, '--device', 0, '--type', 'hdd',
                '--medium', vdi, '--hotpluggable', 'on', '--nonrotational', 'on']
end

Vagrant.configure("2") do |config|
  config.vm.box = ""

  config.vm.define "windows", autostart: false do |win|
    #2.2.0 or later: win.vagrant.plugins = ["winrm", "winrm-elevated"]

    win.vm.provider "virtualbox" do |vb|
      #vb.gui = true
      vb.memory = "2048"

      vb.customize ['modifyvm', :id, '--usb', 'on']
      add_usb_vdi(vb, 'windows')
    end

    #We rely on explicit tar/untar in the Makefile instead of synced_folder.
    win.vm.synced_folder ".", "/vagrant", disabled: true, type: "rsync", rsync__exclude: [".*"]

    win.vm.guest = :windows
    win.vm.communicator = "winrm"
    win.winrm.username = 'vagrant'
    win.winrm.password = 'vagrant'

    win.vm.box = "opentable/win-2012r2-standard-amd64-nocm"
    win.vm.network "forwarded_port", host: 33389, guest: 3389
    win.ssh.extra_args = ['-oHostKeyAlgorithms=+ssh-dss']

    win.vm.provision "prep", type: "shell", inline: <<-SHELL
      echo " ****** Enabling TLS1.2 ******"
      [Net.ServicePointManager]::SecurityProtocol = "tls12, tls11, tls"

      echo " ****** Installing chocolatey ******"
      if (!(Test-Path "$env:SystemDrive\\ProgramData\\Chocolatey\\bin")) {
        iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
      }
      #Need to pull in the chocolatey profile so refreshenv works.
      $env:ChocolateyInstall = Convert-Path "$((Get-Command choco).path)\\..\\.."
      Import-Module "$env:ChocolateyInstall\\helpers\\chocolateyProfile.psm1"
      refreshenv

      echo " ****** Installing .Net 3.5 ******"
      Install-WindowsFeature Net-Framework-Core
      #dism.exe /online /enable-feature /featurename:NetFX3 /all

      echo " ****** Installing needed choco packages ******"
      choco install --forcex86 -y python --version 3.7.5
      choco install -y wixtoolset
      choco install -y git --params "/GitAndUnixToolsOnPath /NoGitLfs"
      refreshenv

      echo " ****** Setting up python venv ******"
      cd \\Users\\vagrant
      python -m venv venv
      . venv\\Scripts\\activate.ps1

      echo " ****** Installing briefcase ******"
      $env:PIP_DISABLE_PIP_VERSION_CHECK=1
      python -m pip install --upgrade pip
      pip install 'briefcase~=0.3'

      echo " ****** Prep done ******"
    SHELL

    win.vm.provision "build", type: "shell", run: "never", inline: <<-SHELL
      echo " ****** Activating python venv ******"
      cd \\Users\\vagrant
      . venv\\Scripts\\activate.ps1
      $env:PIP_DISABLE_PIP_VERSION_CHECK=1

      cd \\vagrant

      echo " ****** Starting installer build ******"
      $env:PYTHONIOENCODING="utf-8"  #Workaround briefcase bug 179.
      briefcase package windows msi

      echo " ****** Build done *******"
    SHELL
    #XXX Package up into an exe (also with zerotier's .msi?):
    #https://www.firegiant.com/wix/tutorial/net-and-net/bootstrapping/

    win.vm.provision "test", type: "shell", run: "never", privileged: false, inline: <<-SHELL
      #XXX error out if \\vagrant\windows\*.msi doesn't exist.
      rm -Fo -ErrorAction SilentlyContinue \\vagrant\\windows\\tests_passed

      echo " ****** Installing ZeroTier ******"
      choco install -y zerotier-one

      echo " ****** Install client ******"
      Start-Process msiexec.exe -Wait -ArgumentList '/I "C:\\vagrant\\windows\\Boundery Client-0.0.1.msi" /qn'

      refreshenv

      echo " ****** Run tests *******"
      cd "\\Users\\vagrant\\AppData\\Local\\Programs\\Boundery Client"
      $env:BOUNDERY_APP_TEST = '1'
      $env:BOUNDERY_ENUM_FIXED = '1' #VirtualBox/libvirt USB devices aren't removable.
      & "\\Users\\vagrant\\AppData\\Local\\Programs\\Boundery Client\\python\\python.exe" -m boundery
      echo "" > \\vagrant\\windows\\tests_passed

      echo " ****** Tests done *******"
    SHELL
  end

  config.vm.define "macos", autostart: false do |mac|
    mac.vm.box = "jhcook/macos-sierra"
    mac.vm.network "forwarded_port", host: 5909, guest: 5900
    #XXX Needed for ZT to actually work in VirtualBox:
    #mac.vm.network "public_network"
    #sudo networksetup -ordernetworkservices "Ethernet Adaptor (en1)" "Ethernet"

    mac.vm.provider "virtualbox" do |vb|
      #vb.gui = true
      vb.memory = "2048"

      vb.customize ['modifyvm', :id, '--ostype', 'MacOS_64']
      vb.customize ['modifyvm', :id, '--usbxhci', 'off']
      vb.customize ['modifyvm', :id, '--usbehci', 'off']

      #Workaround for AMD hosts
      vb.customize ['setextradata', :id, 'VBoxInternal/CPUM/MSRs/MsrBiosSign/First', '0x0000008B']
      vb.customize ['modifyvm', :id, '--cpu-profile', 'Intel Core i7-6700K']
      vb.customize ['modifyvm', :id, '--cpuidset', '00000001', '000106a5', '00100800', '0098e3fd', 'bfebfbff']

      add_usb_vdi(vb, 'macos')
    end

    mac.vm.synced_folder ".", "/vagrant", type: "rsync",
                         rsync__exclude: [".*"], rsync__chown: false

    mac.vm.provision "prep", type: "shell", privileged: false, inline: <<-SHELL
      set -e

      echo " ****** Enabling VNC ******"
      sudo /System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart \
        -activate -configure -access -on \
        -configure -allowAccessFor -allUsers \
        -configure -restart -agent -privs -all

      echo " ****** Enabling Autologin ******"
      #XXX May not be needed thanks to BOUNDERY_VAGRANT_PW=1
      #https://github.com/timsutton/osx-vm-templates/blob/master/scripts/autologin.sh
      echo -e -n '\x0b\xe8\x35\x51\xb3\xd2\xa9\xea\xc4\x7f\x76\x0e' | sudo tee /etc/kcpassword > /dev/null
      sudo chmod 0600 /etc/kcpassword
      sudo /usr/bin/defaults write /Library/Preferences/com.apple.loginwindow autoLoginUser vagrant

      echo " ****** Installing git ******"
      curl -# -L -o /tmp/git.dmg "https://sourceforge.net/projects/git-osx-installer/files/git-2.22.0-intel-universal-mavericks.dmg/download?use_mirror=autoselect"
      VOL=`sudo hdiutil attach /tmp/git.dmg | grep /Volumes/ | cut -f3`
      sudo installer -pkg "$VOL"/git-*.pkg -target /
      sudo hdiutil detach "$VOL"
      rm /tmp/git.dmg

      echo " ****** Installing python ******"
      curl -# -o /tmp/python3.pkg https://www.python.org/ftp/python/3.7.4/python-3.7.4-macosx10.9.pkg
      sudo installer -pkg /tmp/python3.pkg -target /
      rm /tmp/python3.pkg

      echo " ****** Installing Xcode command line tools ******"
      #https://apple.stackexchange.com/questions/107307/how-can-i-install-the-command-line-tools-completely-from-the-command-line
      touch /tmp/.com.apple.dt.CommandLineTools.installondemand.in-progress
      PROD=$(softwareupdate -l |
             grep "\*.*Command Line" |
             head -n 1 | awk -F"*" '{print $2}' |
             sed -e 's/^ *//' |
             tr -d '\n')
      softwareupdate -i "$PROD" --verbose
      rm /tmp/.com.apple.dt.CommandLineTools.installondemand.in-progress

      echo " ****** Setting up python venv ******"
      python3 -m venv venv
      . venv/bin/activate
      export PIP_DISABLE_PIP_VERSION_CHECK=1

      echo " ****** Installing briefcase ******"
      pip install 'briefcase~=0.3'

      echo " ****** Prep done ******"
    SHELL

    mac.vm.provision "build", type: "shell", run: "never", privileged: false, inline: <<-SHELL
      set -e

      echo " ****** Activating python venv ******"
      . venv/bin/activate
      export PIP_DISABLE_PIP_VERSION_CHECK=1

      sudo chown -R vagrant /vagrant #workaround needing 'rsync__chown: false'
      cd /vagrant

      echo " ****** Starting installer build ******"
      rm -rf macOS
      briefcase package macos dmg --no-sign

      echo " ****** Build done *******"
    SHELL

    mac.vm.provision "test", type: "shell", run: "never", privileged: false, inline: <<-SHELL
      set -e

      rm -f /vagrant/macOS/tests_passed

      echo " ****** Installing ZeroTier ******"
      if [ -z "`which zerotier-cli`" ]; then
         curl -# -L -o /tmp/zt.pkg https://download.zerotier.com/dist/ZeroTier%20One.pkg
         sudo installer -pkg /tmp/zt.pkg -target /
         rm /tmp/zt.pkg
      fi

      sudo chown -R vagrant /vagrant #workaround needing 'rsync__chown: false'
      cd /vagrant

      echo " ****** Install client ******"
      VOL=`sudo hdiutil attach "/vagrant/macOS/Boundery Client-0.0.1.dmg" | grep /Volumes/ | cut -f3`

      echo " ****** Run tests *******"
      diskutil mount "BNDRY TEST" #No one is logged in, so we have to manually mount.
      BOUNDERY_APP_TEST=1 BOUNDERY_USE_VAGRANT_PW=1 "$VOL/Boundery Client.app/Contents/MacOS/Boundery Client"
      sudo hdiutil detach "$VOL" -force
      touch /vagrant/macOS/tests_passed

      echo " ****** Tests done *******"
    SHELL
  end
end
