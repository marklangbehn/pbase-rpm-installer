Name: pbase-php-el8-dep
Version: 1.0
Release: 1
Summary: PBase PHP 7 transitive dependency for EL8 and higher
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-php-transitive-dep
Requires: pbase-preconfig-remi-php72

%description
PBase PHP 7 transitive dependency for EL8 and higher, enables remi-repo for PHP 7.2

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

echo "PBase PHP 7 transitive dependency for EL8 and higher"

%files
