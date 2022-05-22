Name: pbase-preconfig-ssh-fail2ban
Version: 1.0
Release: 0
Summary: PBase SSH fail2ban initial setup
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-ssh-fail2ban-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-ssh-fail2ban
Requires: pbase-epel

%description
Configure SSH fail2ban

%prep
%setup -q

%install
mkdir -p "$RPM_BUILD_ROOT"
cp -R * "$RPM_BUILD_ROOT"

%clean
rm -rf "$RPM_BUILD_ROOT"

%pre

%post
# echo "rpm postinstall $1"

fail() {
    echo "ERROR: $1"
    exit 1
}


echo "PBase SSH fail2ban pre-config file create"

echo ""
echo "Next step - optional - change the SSH fail2ban defaults by making a copy "
echo "     of the sample file and editing it. For example:"
echo ""
echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  cp /usr/local/pbase-data/pbase-preconfig-ssh-fail2ban/module-config-samples/pbase_ssh_fail2ban.json ."
echo "  vi pbase_ssh_fail2ban.json"
echo ""

echo "Next step - finish installing SSH fail2ban with:"
echo ""
echo "  yum -y install pbase-ssh-fail2ban"
echo ""

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-ssh-fail2ban/module-config-samples/pbase_ssh_fail2ban.json
