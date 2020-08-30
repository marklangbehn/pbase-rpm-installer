Name: pbase-php-el7-dep
Version: 1.0
Release: 0
Summary: PBase PHP 7 transitive dependencies for EL7 and lower
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-php-transitive-dep
Requires: pbase-preconfig-remi-php72

%description
PBase PHP 7 transitive dependencies for EL7 and lower, enables remi-repo for PHP 7.2

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

echo "PBase PHP 7 transitive dependencies for EL7 and lower, enables remi-repo for PHP 7.2"

%files
