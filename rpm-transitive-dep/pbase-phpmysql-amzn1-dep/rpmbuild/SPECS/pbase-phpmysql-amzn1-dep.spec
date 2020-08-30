Name: pbase-phpmysql-amzn1-dep
Version: 1.0
Release: 0
Summary: PBase PHP application libraries and php-mysql transitive dependencies for Amazon Linux AMI
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-phpmysql-transitive-dep
Requires: php72, php72-common, php72-mysqlnd, php72-gd, php72-fpm, php72-opcache, php72-pdo, php72-mbstring, php72-mcrypt, php72-pecl-apcu, php72-pecl-imagick
## php >= 7.2,php-mbstring,php-gd,php-zip,php-bz2,php-curl,php-xml,php-json,php-intl,php-fpm,php-opcache,php-mysqlnd >= 7.2,php-pdo >= 7.2


%description
PBase PHP application libraries and php-mysql transitive dependencies for Amazon Linux AMI

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

echo "PBase PHP application libraries and php-mysql transitive dependencies for Amazon Linux AMI"

%files
