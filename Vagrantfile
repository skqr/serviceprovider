# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "bento/debian-8.7"
  config.vm.synced_folder ".", "/vagrant", type: "rsync", rsync__exclude: ".git/"  # vagrant rsync-auto
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"
    vb.cpus = 2
  end
  config.vm.provision "shell", path: "./vm/debian_setup.sh"
  config.vm.provision "shell", path: "./vm/python_setup.sh"
end
