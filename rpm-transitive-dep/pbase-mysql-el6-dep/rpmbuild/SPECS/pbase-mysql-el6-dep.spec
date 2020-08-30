Name: pbase-mysql-el6-dep
Version: 1.0
Release: 0
Summary: PBase MySQL transitive dependencies for EL6
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot 

Provides: pbase-mysql-transitive-dep
Requires: mysql,mysql-server

%description
MySQL transitive dependencies for EL6

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

echo "MySQL transitive dependencies for EL6"

%files
