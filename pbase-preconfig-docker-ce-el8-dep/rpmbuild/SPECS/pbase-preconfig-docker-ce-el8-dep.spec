Name: pbase-preconfig-docker-ce-el8-dep
Version: 1.0
Release: 0
Summary: PBase Docker CE transitive dependencies for EL8 and higher
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot 

Provides: pbase-preconfig-docker-ce-transitive-dep
Requires: python3


%description
PBase Docker CE transitive dependencies for EL8 and higher

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

echo "PBase Docker CE transitive dependencies for EL8 and higher"

%files
