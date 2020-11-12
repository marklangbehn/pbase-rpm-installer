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
Configure Crowdsec config file

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

echo ""
echo "PBase Crowdsec module config file:"
echo "Next step - optional - change the Crowdsec default config by making"
echo "    a copy of the config sample file and editing it. For example:"
echo ""
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  cp ../module-config-samples/pbase_crowdsec.json ."
echo "  vi pbase_crowdsec.json"
echo ""
echo "Next step - install Crowdsec with:"
echo ""
echo "  yum -y install pbase-crowdsec"
echo ""

%files
## root only access to pbase configuration directories
%defattr(600,root,root,700)
/usr/local/pbase-data/admin-only/module-config-samples/pbase_crowdsec.json