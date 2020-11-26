Name: pbase-preconfig-crowdsec
Version: 1.0
Release: 0
Summary: PBase Crowdsec config file create
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-crowdsec-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-crowdsec

%description
Add Crowdsec pre-config file

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

echo "PBase Crowdsec pre-config file create"

MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
MODULE_SAMPLES_DIR="/usr/local/pbase-data/pbase-preconfig-crowdsec/module-config-samples"

echo ""
echo "Next step - optional - change the Crowdsec default config by"
echo "    making a copy of the config sample file and editing it. For example:"
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  cp ${MODULE_SAMPLES_DIR}/pbase_crowdsec.json ."
echo "  vi pbase_crowdsec.json"
echo ""
echo "Next step - install Crowdsec with:"
echo ""
echo "  yum -y install pbase-crowdsec"
echo ""

%files
## root only access to pbase configuration directories
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-crowdsec/module-config-samples/pbase_crowdsec.json