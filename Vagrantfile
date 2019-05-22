raise "Run: vagrant plugin install winrm" unless Vagrant.has_plugin?('winrm')
raise "Run: vagrant plugin install winrm-elevated" unless Vagrant.has_plugin?('winrm-elevated')

Vagrant.configure("2") do |config|
  config.vm.box = ""

  config.vm.define "win", autostart: false do |win|
    #2.2.0 or later: win.vagrant.plugins = ["winrm", "winrm-elevated"]

    win.vm.provider "virtualbox" do |vb|
      #vb.gui = true
      vb.memory = "2048"
    end

    win.vm.guest = :windows
    win.vm.communicator = "winrm"
    win.winrm.username = 'vagrant'
    win.winrm.password = 'vagrant'

    win.vm.box = "opentable/win-2012r2-standard-amd64-nocm"
    win.vm.network "forwarded_port", host: 33389, guest: 3389

    win.vm.provision "prep", type: "shell", inline: <<-SHELL
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
      choco install --forcex86 -y python
      choco install -y wixtoolset
      choco install -y git
      refreshenv

      echo " ****** Setting up python venv ******"
      cd \\Users\\vagrant
      python -m venv venv
      . venv\\Scripts\\activate.ps1

      echo " ****** Installing briefcase ******"
      $env:PIP_DISABLE_PIP_VERSION_CHECK=1
      pip install briefcase
    SHELL

    win.vm.provision "build", type: "shell", run: "never", inline: <<-SHELL
      echo " ****** Activating python venv ******"
      cd \\Users\\vagrant
      . venv\\Scripts\\activate.ps1
      $env:PIP_DISABLE_PIP_VERSION_CHECK=1

      echo " ****** Copying source files ******"
      rm -R -Fo client
      mkdir client
      cp -Ex .* \\vagrant\\* client
      cp -R -Fo \\vagrant\\boundery client
      cd client

      echo " ****** Starting installer build ******"
      $env:PYTHONIOENCODING="utf-8"  #Workaround briefcase bug 179.
      python setup.py windows --build

      echo " ****** Copying build artifacts ******"
      mkdir -Fo \\vagrant\\windows
      cp -Fo windows\\Boundery* \\vagrant\\windows

      echo " ****** Build done *******"
      echo "" > \\vagrant\\windows\\builddone
    SHELL

    #Package up into an exe (also with zerotier's .msi?):
    #https://www.firegiant.com/wix/tutorial/net-and-net/bootstrapping/
  end

  config.vm.define "mac", autostart: false do |mac|
    mac.vm.box = "ashiq/osx-10.14"

    mac.vm.provider "virtualbox" do |vb|
      #vb.gui = true
      vb.memory = "2048"
    end

    mac.vm.provider "virtualbox" do |vb|
      vb.customize ['modifyvm', :id, '--ostype', 'MacOS_64']
      vb.customize ['modifyvm', :id, '--paravirtprovider', 'default']
      # Adjust CPU settings according to
      # https://github.com/geerlingguy/macos-virtualbox-vm
      vb.customize ['modifyvm', :id, '--cpuidset',
                   '00000001', '000306a9', '00020800', '80000201', '178bfbff']
      # Disable USB variant requiring Virtualbox proprietary extension pack
      vb.customize ["modifyvm", :id, '--usbehci', 'off', '--usbxhci', 'off']
    end

    mac.vm.provision "prep", type: "shell", inline: <<-SHELL
      pwd
    SHELL

    mac.vm.provision "build", type: "shell", run: "never", inline: <<-SHELL
      echo "build"
    SHELL
  end
end
