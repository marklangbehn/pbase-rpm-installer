Name: pbase-lets-encrypt-fedora-dep
Version: 1.0
Release: 0
Summary: PBase Let's Encrypt transitive dependencies for Fedora 3x
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot 

Provides: pbase-lets-encrypt-transitive-dep
Requires: wget,gcc,cpp,mod_ssl,python3,python3-virtualenv,python3-devel,redhat-rpm-config,libffi-devel,openssl-devel,certbot,certbot-apache

%description
PBase Let's Encrypt transitive dependencies for Fedora 3x

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

echo "PBase Let's Encrypt transitive dependencies for Fedora 3x"

%files