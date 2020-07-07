# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/bionic64"
  config.vm.box_check_update = false
  config.vm.box_version = "<= 20200525.0.0"
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install python3-pip -y
    export ROUTERIP="10.0.2.2"
    pip3 install -r /vagrant/requirements.txt
  SHELL
end
