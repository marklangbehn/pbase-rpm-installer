Name: pbase-golang-el7-dep
Version: 1.0
Release: 0
Summary: PBase Let's Encrypt transitive dependencies for EL7 and lower
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot 

Provides: pbase-golang-transitive-dep
Requires: golang

%description
PBase Go language transitive dependencies for EL7

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

echo "PBase Go language transitive dependencies for EL7"

%files
