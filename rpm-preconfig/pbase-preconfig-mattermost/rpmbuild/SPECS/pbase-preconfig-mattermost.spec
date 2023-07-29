Name: pbase-preconfig-mattermost
Version: 1.0
Release: 1
Summary: PBase Mattermost config file create
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-mattermost-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-mattermost, pbase-preconfig-firewall-enable

%description
Configure PBase Mattermost config file

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

echo "PBase Mattermost pre-config file create"

echo ""
echo "Next step - optional - change the Mattermost server default configuration"
echo "  by editing the sample config file. For example:"
echo ""

echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  cp /usr/local/pbase-data/pbase-preconfig-mattermost/module-config-samples/pbase_mattermost.json ."
echo "  vi pbase_mattermost.json"

echo ""
echo "Next step - install Mattermost with:"
echo "  yum -y install pbase-mattermost"
echo ""

%files
## root only access to pbase configuration directories
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-mattermost/module-config-samples/pbase_mattermost.json