VAGRANT_VERSION = "2"
VM_BOX = "bento/ubuntu-16.04"
USE_GIT_VERSION = false

hosts = [
    {name: "microblog", ip: "192.168.33.10"}
]

Vagrant.configure(VAGRANT_VERSION) do |config|
    config.vm.box = VM_BOX
    config.ssh.insert_key = false

    config.vm.provider "virtualbox" do |vb|
        vb.check_guest_additions = false
        vb.functional_vboxsf = false
    end

    hosts.each_with_index do |elem, index|
        config.vm.define elem[:name] do |machine|
            if USE_GIT_VERSION
            machine.vm.synced_folder ".", "/vagrant", disabled: true
            else
            machine.vm.synced_folder ".", "/opt/microblog", type: "rsync",
                rsync__exclude: File.readlines('.gitignore').each(&:chomp!)
            end
            machine.vm.synced_folder "./vagrant", "/automated"
            machine.vm.network :private_network, ip: elem[:ip]
            machine.vm.hostname = elem[:name]
            machine.vm.provider "virtualbox" do |v|
                v.name = elem[:name]
                v.customize ["modifyvm", :id, "--memory", 1024]
            end
            machine.vm.provision :shell, keep_color: true, path: "automated.sh"
        end
    end
end