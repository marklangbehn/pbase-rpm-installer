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
Requires: pbase-preconfig-virtualbox-transitive-dep,binutils,gcc,make,patch,libgomp,glibc-headers,glibc-devel,bzip2,perl,kernel-devel,kernel-headers


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

## REVISIT -- what is most reliable way to set VirtualBox KERN_DIR and KERN_VER?
## Sometimes 'uname -n' works, but not always.  Using  'ls -1tr /usr/src/kernels' instead.

echo export KERN_DIR='/usr/src/kernels/$(ls -1tr /usr/src/kernels/ | tail -n1)' >> ~/.bashrc
echo export KERN_VER='$(ls -1tr /usr/src/kernels/ | tail -n1)' >> ~/.bashrc

echo "KERN_DIR:                /usr/src/kernels/$(ls -1tr /usr/src/kernels/ | tail -n1)"
echo "KERN_VER:                $(ls -1tr /usr/src/kernels/ | tail -n1)"
echo ""
echo "Pre-config complete for either VirtualBox host or guest. "
echo 'Next step - optional - verify correct $KERN_DIR after install with'
echo '            these commands to check the $KERN_DIR in the .bashrc'
echo '  source /root/.bashrc'
echo '  ls -l $KERN_DIR'
echo '  echo $KERN_VER'
echo ""
echo "Next step - to setup a VirtualBox GUEST system you must do these steps:"
echo ""
echo "  1: Reboot your guest VM to activate the VirtualBox environment variables"
echo "  2: Select the 'Insert the VirtualBox Guest Additions CD Image' menu item"
echo "  3: Click the 'Run' dialog button when prompted to rebuild the guest kernel"
echo "  4: Reboot your guest VM to see the Guest Additions running "
echo ""
echo "Next step - to setup a VirtualBox HOST system you must run three more commands:"
echo ""
echo "  yum -y install VirtualBox-6.1"
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
