Name: pbase-preconfig-firewall-enable
Version: 1.0
Release: 1
Summary: PBase firewall port pre-config file create
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-firewall-enable-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-firewall-enable
Requires: pbase-epel, jq

%description
Configure firewall port pre-config file create

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

echo "PBase firewall port pre-config file create"

MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
MODULE_SAMPLES_DIR="/usr/local/pbase-data/pbase-preconfig-firewall-enable/module-config-samples"

CONFIG_FILENAME="pbase_firewall_enable.json"
echo "Firewall config:         ${MODULE_CONFIG_DIR}/${CONFIG_FILENAME}"

/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/${CONFIG_FILENAME}  ${MODULE_CONFIG_DIR}/


echo "Next step - recommended - review the firewall"
echo "  default ports by editing the pbase_firewall_enable.json file."
echo "  Enable more ports with the additionalPorts json field in this file."
echo "   additionalPorts: [ 28800, 29900 ]  "
echo "  For example:"
echo ""
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  vi pbase_firewall_enable.json"

echo ""
echo "Next step - start firewall with:"
echo ""
echo "  yum -y install pbase-firewall-enable"
echo ""

%files
## root only access to pbase configuration directories
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-firewall-enable/module-config-samples/pbase_firewall_enable.json