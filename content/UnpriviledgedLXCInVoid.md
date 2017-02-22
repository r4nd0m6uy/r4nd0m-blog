Title: Unpriviledged containers in Void Linux
Date: 2017-02-21 19:00
Category: Sysadmin
Tags: tutorial, linux, lxc

It seems that I was not the first one to struggle to make unprivildged
linux containers working in 
[Void Linux](http://www.voidlinux.eu/download/). In systemd/Linux
distributions, the process is straight forward has systemd handles
things automagically for you (mostly everthing about cgroup) when in
Void you have to configure few things by yourself.

I want to give some pointers to have the bare minimal to have a
container starting in unpriviledged mode in distribution that use a 
minimal init system and more precisely here, Void Linux.

# Prerequists
First we need few services installed on the host. Of course lxc but also
cgmanager to take care of the cgroups, dbus for IPC communication
between cgmanager and the bridge-utils to create a network interface for
our container:

    :::sh
    sudo xbps-install cgmanager dbus bridge-utils lxc

Configure runit to start dbus and cgmanager automatically at startup,
also start them right away:

    :::sh
	sudo ln -s /etc/sv/dbus/ /var/service/
	sudo ln -s /etc/sv/cgmanager/ /var/service/
	sudo sv start dbus
	sudo sv start cgmanager

Now we need to configure the subuid, subgid mapping. First create the
two */etc/sub{u,g}id* and give the read permission for all others:

    :::sh
	sudo touch /etc/sub{u,g}id
	sudo chmod o+r /etc/sub{g,u}id

Then map your user to the lxc g/u ids:

    :::sh
	sudo usermod --add-subuids 100000-165536 $USER
	sudo usermod --add-subgids 100000-165536 $USER

We also need a bridge interface to connect our container, my host
network interface is *enp0s25* and the bridge will be *lxcbr0*.

    :::sh
	sudo brctl addbr lxcbr0
	sudo brctl addif lxcbr0 enp0s25
	sudo ifconfig lxcbr0 up

If you don't want to reconfigure your bridge at each boot, you could
create a runit service for that. Now create a default lxc configuration
in *~/.config/lxc/default.conf* containing everything we have just done:

    :::txt
	lxc.network.type = veth
	lxc.network.link = lxcbr0
	lxc.network.flags = up
	lxc.network.hwaddr = 00:16:3e:BB:CC:DD
	lxc.id_map = u 0 100000 65536
	lxc.id_map = g 0 100000 65536

Now your host system should be ready to run unpriviledged container.

# Creating and starting a container
First create a cgroup crontroller for your user and give the right
permission with cgm. **This has to be done at each boot!** For 
convenience, I suggest to put it in a script or create a runit service.

    :::sh
	sudo cgm create all $USER
	sudo cgm chown all $USER $(id -u) $(id -g)

Then move your current process to the created controller. **This has to
be done each time you open a new shell!**

    :::sh
	cgm movepid all $USER $$

Now lxc should be able to work correcly with cgroups, you can create a 
new container:

    :::sh
	lxc-create -t download -n ubuntu-xenial
	...
	<Fill requested fields>
	...

Once the creation process is done, simply start the container and attach
to it:

    :::sh
	lxc-start -n ubuntu-xenial
	lxc-attach -n ubuntu-xenial

You should now be inside your container, hurray!

    :::sh
	root@ubuntu-xenial:/# cat /etc/issue
	Ubuntu 16.04.2 LTS \n \l


# Starting lxc after a new boot
Unfortunately the configuration is not persistent and some operation
have to be done manually. As I don't start my container all the time, I
don't want to create a runit service, that's why I use a little script:

    :::sh
    #!/bin/sh
	sudo cgm create all $USER
	sudo cgm chown all $USER $(id -u) $(id -g)
	sudo brctl addbr lxcbr0
	sudo brctl addif lxcbr0 enp0s25
	sudo ifconfig lxcbr0 up
	cgm movepid all $USER $$
	lxc-start -n ubuntu-xenial

# Further reading
Some articles that helped me solving this issue:

* [https://s3hh.wordpress.com/2014/03/25/introducing-cgmanager/](https://s3hh.wordpress.com/2014/03/25/introducing-cgmanager/)
* [https://stgraber.org/2014/01/17/lxc-1-0-unprivileged-containers/](https://stgraber.org/2014/01/17/lxc-1-0-unprivileged-containers/)

# Next step
Now you have your container starting, [you probably want to configure
the network]({filename}/WlanNatForLxc.md).
