Name: pbase-preconfig-meanstack
Version: 1.0
Release: 0
Summary: PBase MEAN stack pre-configuration
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-meanstack
Requires: pbase-apache,pbase-preconfig-nodejs12,pbase-preconfig-mongodb-org

%description
Pre-configure PBase MEAN stack components

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

echo "PBase MEAN stack pre-configuration complete, Apache httpd service installed"
echo "Next step - install MEAN stack components:"
echo ""
echo "  yum -y install nodejs"
echo "  yum -y install mongodb"

%files
