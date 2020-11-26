Name: pbase-preconfig-realtime-kernel
Version: 1.0
Release: 0
Summary: PBase realtime kernel pre-configure
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-realtime-kernel-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-realtime-kernel
Requires: centos-release-stream

%description
Configure PBase realtime kernel pre-configure

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

echo "PBase realtime kernel pre-configure"

##TODO require CentOS8 Stream

/bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig-realtime-kernel/etc-yum-repos-d/CentOS-Stream-RT.repo /etc/yum.repos.d/

if [[ -e "/etc/yum.repos.d/CentOS-Stream-RT.repo" ]] ; then
  ## change repo enable flag: enabled=0
  echo "Enabling Stream-RT:      /etc/yum.repos.d/CentOS-Stream-RT.repo"
  /bin/sed -i "s/enabled=0/enabled=1/" /etc/yum.repos.d/CentOS-Stream-RT.repo
else
  echo "Could not find repo:     /etc/yum.repos.d/CentOS-Stream-RT.repo"
fi


echo "Next step - install kernel and rt setup utilities with:"
echo ""
echo "  yum -y install pbase-realtime-kernel"
echo ""

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-realtime-kernel/etc-yum-repos-d/CentOS-Stream-RT.repo
