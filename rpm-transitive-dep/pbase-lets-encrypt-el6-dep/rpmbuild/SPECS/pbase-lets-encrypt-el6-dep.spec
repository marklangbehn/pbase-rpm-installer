Name: pbase-lets-encrypt-el6-dep
Version: 1.0
Release: 1
Summary: PBase Let's Encrypt transitive dependencies for EL6
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot 

Provides: pbase-lets-encrypt-transitive-dep
Requires: mod_ssl,redhat-rpm-config,libffi-devel,openssl-devel,python34 python34-devel python34-tools

%description
PBase Let's Encrypt transitive dependencies for EL6

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

echo "PBase Let's Encrypt transitive dependencies for EL6"

%files
