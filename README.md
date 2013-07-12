drunken-control
===============

Software to control heating elements in a home brewery


Requirements
============

Needs a ramdisk to store current information. Add the following to /etc/fstab
  tmpfs           /mnt/ramdisk    tmpfs   size=1M,noatime,mode=1777       0       0

Add 1wire and ic2 modules
  edit /etc/modules:
  # /etc/modules: kernel modules to load at boot time.
  #
  # This file contains the names of kernel modules that should be loaded
  # at boot time, one per line. Lines beginning with "#" are ignored.
  # Parameters can be specified after the module name.
  
  snd-bcm2835
  i2c-bcm2708
  i2c-dev
  w1-gpio
  w1-therm

  comment out everthing in /etc/modprobe.d/raspi-blacklist.conf
  
  

unneeded, but nice on a bare raspbian:
aptitude install vim digitemp wicd-curses wicd i2c-tools git tmuxsu

#required
aptitude install python-pip python-smbus python-mysqldb
pip install flask pyyaml tornado
