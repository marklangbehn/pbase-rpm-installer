Name: pbase-epel-el10-dep
Version: 1.0
Release: 0
Summary: PBase EPEL repo transitive dependencies for EL10/CentOS Stream 10
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-epel-transitive-dep
Requires: epel-release
##Requires: epel-release, epel-next-release
## TODO - add epel-next-release when it is available

%description
EPEL repo transitive dependency for EL10/CentOS Stream 10

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

echo "EPEL repo transitive dependencies for EL10/CentOS Stream 10"

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

elif [[ -e "/etc/yum.repos.d/almalinux-powertools.repo" ]] ; then
  echo "Enabling PowerTools:     /etc/yum.repos.d/almalinux-powertools.repo"
  /bin/sed -i "s/enabled=0/enabled=1/" /etc/yum.repos.d/almalinux-powertools.repo

elif [[ -e "/etc/yum.repos.d/almalinux-crb.repo" ]] ; then
  echo "Enabling CRB:            /etc/yum.repos.d/almalinux-crb.repo"
  /bin/sed -i "s/enabled=0/enabled=1/" /etc/yum.repos.d/almalinux-crb.repo

else
 echo "Next step optional, enable CodeReady Builder with"
 echo "  ...on CentOS Stream 10 and other EL10 derivatives:"
 echo "    dnf config-manager --set-enabled crb"
 
## echo "  ...on Red Hat Entrerprise Linux:"
## echo "    subscription-manager repos --enable=codeready-builder-for-rhel-8-x86_64-rpms"

#  echo "Could not find repo:     /etc/yum.repos.d/CentOS-PowerTools.repo"
fi

%files