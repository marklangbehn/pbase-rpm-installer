Name: pbase-preconfig-vault
Version: 1.0
Release: 0
Summary: PBase Vault config file create
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-vault-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-vault

%description
Configure PBase Vault installation file

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

echo "PBase Vault config file create"

echo ""
echo "PBase SSH module config file:"
echo "Next step - optional - change the Vault default config by making a copy "
echo "     of the sample file and editing it. For example:"
echo ""
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  cp ../module-config-samples/pbase_vault.json ."
echo "  vi pbase_vault.json"
echo ""

echo "Next step - install Vault with:"
echo ""
echo "  yum -y install pbase-vault"
echo ""

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/admin-only/module-config-samples/pbase_vault.json
