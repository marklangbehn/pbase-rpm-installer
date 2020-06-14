Name: pbase-mysql-amzn1-dep
Version: 1.0
Release: 0
Summary: PBase MySQL transitive dependencies for Amazon Linux AMI
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot 

Provides: pbase-mysql-transitive-dep
Requires: mysql57, mysql57-server

%description
MySQL transitive dependencies for Amazon Linux AMI

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

echo "MySQL transitive dependencies for Amazon Linux AMI"

%files
