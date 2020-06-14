Name: pbase-preconfig-virtualbox-el7-dep
Version: 1.0
Release: 0
Summary: PBase VirtualBox transitive dependencies for EL7
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-virtualbox-transitive-dep
Requires: dkms,fontforge


%description
PBase VirtualBox transitive dependencies for EL7

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

echo "PBase VirtualBox transitive dependencies for EL7 and lower"

%files
