Name: pbase-epel-fedora-dep
Version: 1.0
Release: 0
Summary: PBase EPEL repo transitive dependencies for Fedora 3x
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot 

Provides: pbase-epel-transitive-dep
## Requires:
## does not use Requires because Fedora 3x already includes EPEL

%description
EPEL repo transitive dependencies for Fedora 3x

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

echo "EPEL repo transitive dependency for Fedora 3x"
## no config needed for Fedora

%files
