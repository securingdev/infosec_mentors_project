# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "ubuntu/trusty64"

  config.vm.provider "virtualbox" do |vb, override|
    vb.cpus = 1
    vb.gui = false
    vb.memory = "1024"

    # Share a folder to the guest VM, types: docker, nfs, rsync, smb, virtualbox
    # Windows supports: smb
    # Mac supports: rsync, nfs
    # override.vm.synced_folder host_folder.to_s, guest_folder.to_s, type: "smb"
    override.vm.synced_folder "./provision", "/vagrant"
    override.vm.synced_folder ".", "/var/www/infosec_mentor_project"

    override.vm.network "forwarded_port", guest: 5432, host: 5432 # postgres
    override.vm.network "forwarded_port", guest: 80, host: 8080 # nginx
    override.vm.network "forwarded_port", guest: 80, host: 8000 # uwsgi
    override.vm.network "forwarded_port", guest: 5000, host: 5000 # Flask

  end

  config.vm.provision :shell, path: "./provision/bootstrap.sh"
end
