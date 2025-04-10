---
author: Min-Ye Zhang
categories: tool
comments: true
date: "2024-10-21 19:19 +0200"
math: false
tags: Ubuntu Linux
title: Upgrade Ubuntu LTS on a work laptop
---

## Background

The HP laptop provided by the institute has decent specs (i7-10850U,
32GB RAM, 500GB SSD), but I haven’t used it much because I’m not a fan
of the pre-installed Ubuntu. Recently, my CI pipeline on GitHub, which
uses the Intel compiler on Ubuntu, started failing. To debug it, having
a local Ubuntu environment, either as the host or in a virtual machine,
would be more convenient. So I think this is a good opportunity to
upgrade the laptop and set up virtual machines that closely match the CI
environment.

## Start upgrade after a long time

The pre-installed Ubuntu is 18.04 LTS, which is a bit old. The one used
in CI is 22.04 LTS. Although it is not necessary to upgrade to the
latest since the debug will be in virtual machine, I think it is a good
idea to upgrade when the machine is still "clean".

The upgrade follows [official
documentation](https://ubuntu.com/server/docs/how-to-upgrade-your-release).
Here I record some troubleshooting.

Error in `update`

    $ sudo apt update
    Err:1 http://dl.google.com/linux/chrome/deb stable InRelease
      The following signatures couldn't be verified because the public key is not available: NO_PUBKEY XXYYZZ

Fix[^1]

``` shell
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys XXYYZZ
```

Error in `upgrade`

    $ sudo apt upgrade
    E: Could not get lock /var/lib/dpkg/lock-frontend - open (11: Resource temporarily unavailable)
    E: Unable to acquire the dpkg frontend lock, is another process using it

Fix[^2]

``` shell
sudo lsof /var/lib/dpkg/lock-frontend
# PID 3000 using lock-frontend
kill -9 3000
ps aux | grep -i apt
# Kill every PID

# Remove lock files
sudo rm /var/lib/apt/lists/lock
sudo rm /var/cache/apt/archives/lock
sudo rm /var/lib/dpkg/lock
sudo rm /var/lib/dpkg/lock-frontend
```

Error in `do-release-upgrade`

    $ sudo do-release-upgrade
    Checking for a new Ubuntu release
    In /etc/update-manager/release-upgrades
    Prompt is set to never so upgrading is not possible.

Fix:[^3] Edit `/etc/update-manager/release-upgrade`, change
`Prompt=never` to

    Prompt=lts

First run of release upgrade leads me to 20.04. To land in 22.04, I need
to trigger it again.

## Install necessary software

### General tools

``` shell
sudo apt -y install \
  git tig duf ripgrep fd-find htop fzf net-tools curl \
  environment-modules cmake gfortran \
  python3 python-is-python3
```

Also install GNOME tweaks to modify caps lock key and other stuff.

``` shell
sudo apt -y install gnome-tweaks
```

### VirtualBox

``` shell
sudo apt -y install virtualbox virtualbox-ext-pack
```

### Intel oneAPI through apt

``` shell
wget -O- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB \
  | gpg --dearmor | sudo tee /usr/share/keyrings/oneapi-archive-keyring.gpg > /dev/null
# add signed entry to apt sources and configure the APT client to use Intel repository:
echo "deb [signed-by=/usr/share/keyrings/oneapi-archive-keyring.gpg] https://apt.repos.intel.com/oneapi all main" \
  | sudo tee /etc/apt/sources.list.d/oneAPI.list
sudo apt-get update --allow-unauthenticated -o Dir::Etc::sourcelist="sources.list.d/oneAPI.list" -o APT::Get::List-Cleanup="0"

sudo apt-get install -y build-essential cmake
sudo apt-get install -y \
  intel-oneapi-compiler-dpcpp-cpp \
  intel-oneapi-compiler-fortran \
  intel-oneapi-mkl intel-oneapi-mkl-devel \
  intel-oneapi-mpi intel-oneapi-mpi-devel
# or simply install intel-basekit and intel-hpckit
```

As of writing (2024-10-21), it installs `ifx`, `icx` and `icpx`
compilers of version 2024.2.1. `ifort` is still included (2021.13.1),
but will be discontinued in late 2024. The Intel MPI is also installed
and provides MPI wrappers for all the compilers, including `mpiicc` and
`mpiicpc`. However, they will not work because the underlying compiler
is missing.

One can pin the apt packages by writing files under
`/etc/apt/preferences.d`. sudo is required.

``` shell
packages=(
  intel-oneapi-common-vars
  intel-oneapi-compiler-dpcpp-cpp
  intel-oneapi-compiler-fortran
  intel-oneapi-mkl intel-oneapi-mkl-devel
)

for package in ${packages[@]}; do
  sudo cat > /etc/apt/preferences.d/$package << EOF
Package: $package
Pin: version 2024.2.*
Pin-Priority: 999
EOF
done

for package in intel-oneapi-mpi intel-oneapi-mpi-devel; do
  sudo cat > /etc/apt/preferences.d/$package << EOF
Package: $package
Pin: version 2021.13.1-*
Pin-Priority: 999
EOF
done
```

Then those packages will not be upgraded when `apt upgrade` is issued.

### Turn on SSH port

``` shell
sudo apt install openssh-server
```

Add to `/etc/ssh/sshd_config`

    PubkeyAuthentication yes
    PasswordAuthentication no

### Zerotier for tunneling

``` shell
curl -s https://install.zerotier.com | sudo bash
sudo zerotier-cli join <network-ID>
```

------------------------------------------------------------------------

[^1]: <https://unix.stackexchange.com/questions/219341/how-to-apt-delete-repository>

[^2]: <https://www.geeksforgeeks.org/how-to-fix-unable-to-acquire-the-dpkg-frontend-lock-error-in-ubuntu/>

[^3]: <https://askubuntu.com/questions/115913/disable-ubuntu-update-managers-new-version-warning>
