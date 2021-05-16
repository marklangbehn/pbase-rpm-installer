Name: pbase-preconfig-docker-ce-el7-dep
Version: 1.0
Release: 0
Summary: PBase Docker CE transitive dependencies for EL7 and lower
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot 

Provides: pbase-preconfig-docker-ce-transitive-dep
Requires: python-pip

%description
PBase Docker CE transitive dependencies for EL7 and lower

%prep

%install

%clean

%pre

%post
echo "rpm postinstall $1"

fail() {
    echo "ERROR: $1"
    exit 1
}

echo "PBase Docker CE transitive dependencies for EL7 and lower"

%files
