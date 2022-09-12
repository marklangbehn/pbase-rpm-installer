Name: pbase-preconfig-ssh-port
Version: 1.0
Release: 1
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

MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
MODULE_SAMPLES_DIR="/usr/local/pbase-data/pbase-preconfig-ssh-port/module-config-samples"
CONFIG_FILENAME="pbase_ssh_port.json"

echo "SSH default port config: ${MODULE_CONFIG_DIR}/${CONFIG_FILENAME}"
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/${CONFIG_FILENAME}  ${MODULE_CONFIG_DIR}/

echo ""
echo "Next step - optional - customize the SSH default port provided"
echo "    under 'module-config.d' by editing the JSON text file. For example:"
echo ""
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  vi ${CONFIG_FILENAME}"
echo ""

echo "Next step - install SSH with:"
echo ""
echo "  yum -y install pbase-ssh-port"
echo ""

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-ssh-port/module-config-samples/pbase_ssh_port.json
