Name: pbase-preconfig-virtualbox
Version: 1.0
Release: 0
Summary: PBase VirtualBox preconfigure
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-virtualbox-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-virtualbox
Requires: binutils,gcc,make,patch,libgomp,glibc-headers,glibc-devel,bzip2,perl,kernel-devel,kernel-headers,pbase-preconfig-virtualbox-transitive-dep


%description
Configure yum repo for current VirtualBox version, and kernel build tools

%prep
%setup -q

%install
mkdir -p "$RPM_BUILD_ROOT"
cp -R * "$RPM_BUILD_ROOT"

%clean
rm -rf "$RPM_BUILD_ROOT"

%pre

%post
echo "rpm postinstall $1"

fail() {
    echo "ERROR: $1"
    exit 1
}

check_linux_version() {
  AMAZON1_RELEASE=""
  AMAZON2_RELEASE=""
  if [[ -e "/etc/system-release" ]]; then
    SYSTEM_RELEASE="$(cat /etc/system-release)"
    AMAZON1_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux AMI')"
    AMAZON2_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux release 2')"
    echo "system-release:          ${SYSTEM_RELEASE}"
  fi

  FEDORA_RELEASE=""
  if [[ -e "/etc/fedora-release" ]]; then
    FEDORA_RELEASE="$(cat /etc/fedora-release)"
    echo "fedora_release:          ${FEDORA_RELEASE}"
  fi

  REDHAT_RELEASE_DIGIT=""
  if [[ -e "/etc/redhat-release" ]]; then
    REDHAT_RELEASE_DIGIT="$(cat /etc/redhat-release | grep -oE '[0-9]+' | head -n1)"
    echo "REDHAT_RELEASE_DIGIT:    ${REDHAT_RELEASE_DIGIT}"
  elif [[ "$AMAZON1_RELEASE" != "" ]]; then
    echo "AMAZON1_RELEASE:         $AMAZON1_RELEASE"
    REDHAT_RELEASE_DIGIT="6"
    echo "REDHAT_RELEASE_DIGIT:    ${REDHAT_RELEASE_DIGIT}"
  elif [[ "$AMAZON2_RELEASE" != "" ]]; then
    echo "AMAZON2_RELEASE:         $AMAZON2_RELEASE"
    REDHAT_RELEASE_DIGIT="7"
    echo "REDHAT_RELEASE_DIGIT:    ${REDHAT_RELEASE_DIGIT}"
  fi
}


echo "PBase VirtualBox pre-configuration"

## check which version of Linux is installed
check_linux_version

if [[ "$FEDORA_RELEASE" != "" ]]; then
  echo "Fedora release found"
fi

echo "virtualbox.repo:         /etc/yum.repos.d/virtualbox.repo"

if [[ "$FEDORA_RELEASE" == "" ]]; then
  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig-virtualbox/etc-yum-repos-d/el7/virtualbox.repo /etc/yum.repos.d/virtualbox.repo
else
  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig-virtualbox/etc-yum-repos-d/fedora/virtualbox.repo /etc/yum.repos.d/virtualbox.repo
fi


echo "Setting env variable:    KERN_DIR"

## TODO -- KERN_DIR DOESN'T ALWAYS WORK -- NEEDS EXACT PATH -- give helpful msg for now

echo export KERN_DIR=/usr/src/kernels/`uname -r` >> ~/.bashrc
echo export KERN_VER=`uname -r` >> ~/.bashrc

echo "KERN_DIR:                /usr/src/kernels/`uname -r`"
echo "KERN_VER:                `uname -r`"
echo ""
echo 'Next step - optional - verify correct $KERN_DIR after install with "source /root/.bashrc" followed by "ls -l $KERN_DIR" to see if correct value is set in /root/.bashrc'
echo ""
echo "Pre-config complete for either host or guest. "
echo "Next, to setup a VirtualBox host system you must run three more commands:"
echo ""
echo "  yum -y install VirtualBox-6.1"
#echo "  service vboxdrv setup"
echo "  /usr/lib/virtualbox/vboxdrv.sh setup"
echo "  usermod -a -G vboxusers myregularusername"
echo ""
echo "Then, logged in as your regular desktop user launch app with:"
echo "  VirtualBox"


%preun
echo "rpm preuninstall"

## remove the repo file added by script
/bin/rm -f /etc/yum.repos.d/virtualbox.repo


%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-preconfig-virtualbox/etc-yum-repos-d/el7/virtualbox.repo
/usr/local/pbase-data/pbase-preconfig-virtualbox/etc-yum-repos-d/fedora/virtualbox.repo
