Name: pbase-epel-el8-dep
Version: 1.0
Release: 1
Summary: PBase EPEL repo transitive dependencies for EL8/CentOS 8
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot 

Provides: pbase-epel-transitive-dep
Requires: epel-release

%description
EPEL repo transitive dependency for EL8/CentOS 8

%prep

%install

%clean

%pre

%post
#echo "rpm postinstall $1"

fail() {
    echo "ERROR: $1"
    exit 1
}

echo "EPEL repo transitive dependencies for EL8/CentOS 8"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

## Enable PowerTools repo - depending on filename
## change repo enable flag: enabled=0

if [[ -e "/etc/yum.repos.d/CentOS-PowerTools.repo" ]] ; then
  echo "Enabling PowerTools:     /etc/yum.repos.d/CentOS-PowerTools.repo"
  /bin/sed -i "s/enabled=0/enabled=1/" /etc/yum.repos.d/CentOS-PowerTools.repo

elif [[ -e "/etc/yum.repos.d/CentOS-Linux-PowerTools.repo" ]] ; then
  echo "Enabling PowerTools:     /etc/yum.repos.d/CentOS-Linux-PowerTools.repo"
  /bin/sed -i "s/enabled=0/enabled=1/" /etc/yum.repos.d/CentOS-Linux-PowerTools.repo

elif [[ -e "/etc/yum.repos.d/CentOS-Stream-PowerTools.repo" ]] ; then
  echo "Enabling PowerTools:     /etc/yum.repos.d/CentOS-Stream-PowerTools.repo"
  /bin/sed -i "s/enabled=0/enabled=1/" /etc/yum.repos.d/CentOS-Stream-PowerTools.repo

elif [[ -e "/etc/yum.repos.d/Rocky-PowerTools.repo" ]] ; then
  echo "Enabling PowerTools:     /etc/yum.repos.d/Rocky-PowerTools.repo"
  /bin/sed -i "s/enabled=0/enabled=1/" /etc/yum.repos.d/Rocky-PowerTools.repo

else
  echo "Could not find repo:     /etc/yum.repos.d/CentOS-PowerTools.repo"
fi

%files
