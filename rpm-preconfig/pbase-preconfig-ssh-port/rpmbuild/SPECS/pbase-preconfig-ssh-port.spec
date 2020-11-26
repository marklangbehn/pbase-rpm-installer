Name: pbase-preconfig-ssh-port
Version: 1.0
Release: 0
Summary: PBase SSH port config file create
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-ssh-port-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-ssh-port

%description
Configure SSH port pre-config file

%prep
%setup -q

%install
mkdir -p "$RPM_BUILD_ROOT"
cp -R * "$RPM_BUILD_ROOT"

%clean
rm -rf "$RPM_BUILD_ROOT"

%pre

%post
echo "rpm postinstall $1"

fail() {
    echo "ERROR: $1"
    exit 1
}

echo "PBase SSH port pre-config file create"

echo ""
echo "Next step - optional - change the SSH default port by making a copy "
echo "     of the sample file and editing it. For example:"
echo ""
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  cp /usr/local/pbase-data/pbase-preconfig-ssh-port/module-config-samples/pbase_ssh_port.json ."
echo "  vi pbase_ssh_port.json"
echo ""

echo "Next step - install SSH with:"
echo ""
echo "  yum -y install pbase-ssh-port"
echo ""

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-ssh-port/module-config-samples/pbase_ssh_port.json
