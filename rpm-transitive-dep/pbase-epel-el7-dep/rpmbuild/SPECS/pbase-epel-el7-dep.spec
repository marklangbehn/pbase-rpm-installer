Name: pbase-epel-el7-dep
Version: 1.0
Release: 0
Summary: PBase EPEL repo transitive dependencies for EL7/CentOS 7
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot 

Provides: pbase-epel-transitive-dep
Requires: epel-release

%description
EPEL repo transitive dependency for EL7/CentOS 7

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

echo "EPEL repo transitive dependencies for EL7/CentOS 7"

%files
