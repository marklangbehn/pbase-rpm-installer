Name: pbase-phpmysql-el7-dep
Version: 1.0
Release: 0
Summary: PBase PHP application libraries and php-mysql transitive dependencies for EL6
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-phpmysql-transitive-dep
Requires: php,php-mbstring,php-gd,php-zip,php-pecl-zip,php-bz2,php-curl,php-xml,php-json,php-intl,php-fpm,php-opcache,php-mysql,php-pdo

%description
PBase PHP application libraries and php-mysql transitive dependencies for EL6

%prep

%install

%clean

%pre

%post
# echo "rpm postinstall $1"

fail() {
    echo "ERROR: $1"
    exit 1
}

echo "PBase PHP application libraries and php-mysql transitive dependencies for EL6"

%files
