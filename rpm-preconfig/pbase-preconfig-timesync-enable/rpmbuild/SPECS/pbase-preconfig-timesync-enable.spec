Name: pbase-preconfig-timesync-enable
Version: 1.0
Release: 0
Summary: PBase NTP/Chrony config file create
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-timesync-enable-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-timesync-enable
Requires: pbase-epel

%description
Configure NTP/Chrony config file

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

echo "PBase NTP/Chrony timesync config file"

echo ""
echo "Next step - optional - change the default time-zone from UTC"
echo "    by editing the pre-config file. For example:"
echo ""
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  vi pbase_timesync_enable.json"
echo ""
echo "Next step - finish NTP/Chrony configuration with:"
echo ""
echo "  yum -y install pbase-timesync-enable"
echo ""

%files
## root only access to pbase configuration directories
%defattr(600,root,root,700)
/usr/local/pbase-data/admin-only/module-config.d/pbase_timesync_enable.json
