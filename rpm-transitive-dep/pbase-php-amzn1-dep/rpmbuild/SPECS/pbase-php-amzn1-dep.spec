Name: pbase-php-amzn1-dep
Version: 1.0
Release: 0
Summary: PBase PHP 7 transitive dependencies for Amazon Linux AMI
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-php-transitive-dep

%description
PBase PHP 7.2 transitive dependencies for Amazon Linux AMI

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

echo "PBase PHP 7.2 transitive dependencies for Amazon Linux AMI"
##TODO enable EPEL on Amazon Linux AMI

%files
