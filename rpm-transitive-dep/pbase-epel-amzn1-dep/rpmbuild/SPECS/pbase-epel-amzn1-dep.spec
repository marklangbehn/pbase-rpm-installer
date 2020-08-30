Name: pbase-epel-amzn1-dep
Version: 1.0
Release: 0
Summary: PBase EPEL repo transitive dependencies for Amazon Linux AMI
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot 

Provides: pbase-epel-transitive-dep
## Requires:
## does not use Requires because amzn1 AMI uses 'yum-config-manager' command to enable EPEL

%description
EPEL repo transitive dependency for Amazon Linux AMI

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

echo "EPEL repo transitive dependencies for Amazon Linux AMI"
echo "Executing:               yum-config-manager --enable epel"

yum-config-manager --enable epel

echo "Complete"
%files
