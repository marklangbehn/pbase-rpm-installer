Name: pbase-lets-encrypt-el10-dep
Version: 1.0
Release: 0
Summary: PBase Let's Encrypt transitive dependencies for EL10 and higher
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-lets-encrypt-el10-dep-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot 

Provides: pbase-lets-encrypt-transitive-dep
Requires: mod_ssl,python3,augeas-libs

%description
PBase Let's Encrypt transitive dependencies for EL10 and higher

%global source_date_epoch_from_changelog 0

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

echo "PBase Let's Encrypt transitive dependencies for EL10 and higher"

echo "Adding Service:          /usr/lib/systemd/system/certbot-renew.service"
/bin/cp --no-clobber /usr/local/pbase-data/pbase-lets-encrypt-el10-dep/usr-lib-systemd-system/certbot-renew.service /usr/lib/systemd/system/

echo "Renewal Timer:           /usr/lib/systemd/system/certbot-renew.timer"
/bin/cp --no-clobber /usr/local/pbase-data/pbase-lets-encrypt-el10-dep/usr-lib-systemd-system/certbot-renew.timer /usr/lib/systemd/system/

echo "Renewal Config:          /etc/sysconfig/certbot"
/bin/cp --no-clobber /usr/local/pbase-data/pbase-lets-encrypt-el10-dep/etc-sysconfig/certbot /etc/sysconfig/

echo "Enabling Timer:          certbot-renew.timer"
/bin/systemctl daemon-reload
/bin/systemctl enable --now certbot-renew.timer

echo "Creating Python virtual env with:    python3 -m venv /opt/certbot/"
python3 -m venv /opt/certbot/

echo "pip install --upgrade pip"
/opt/certbot/bin/pip --quiet install --upgrade pip

echo "pip install certbot"
/opt/certbot/bin/pip --quiet install certbot

echo "pip install certbot-apache"
/opt/certbot/bin/pip --quiet install certbot-apache

## add symlink
ln -s /opt/certbot/bin/certbot /usr/bin/

echo "Let's Encrypt certbot installed:"
ls -l /usr/bin/certbot

%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-lets-encrypt-el10-dep/usr-lib-systemd-system/certbot-renew.service
/usr/local/pbase-data/pbase-lets-encrypt-el10-dep/usr-lib-systemd-system/certbot-renew.timer
/usr/local/pbase-data/pbase-lets-encrypt-el10-dep/etc-sysconfig/certbot