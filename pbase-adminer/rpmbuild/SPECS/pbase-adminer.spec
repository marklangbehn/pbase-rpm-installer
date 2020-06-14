Name: pbase-adminer
Version: 1.0
Release: 0
Summary: PBase Adminer DB interface
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-adminer-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-adminer
Requires: httpd,apr-util-pgsql,php,php-gd,php-pdo,php-xml,php-mysqli,php-pgsql,pbase-apache


%description
Install Adminer DB interface

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

check_linux_version() {
  AMAZON1_RELEASE=""
  AMAZON2_RELEASE=""
  if [[ -e "/etc/system-release" ]]; then
    SYSTEM_RELEASE="$(cat /etc/system-release)"
    AMAZON1_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux AMI')"
    AMAZON2_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux release 2')"
    echo "system-release:          ${SYSTEM_RELEASE}"
  fi

  FEDORA_RELEASE=""
  if [[ -e "/etc/fedora-release" ]]; then
    FEDORA_RELEASE="$(cat /etc/fedora-release)"
    echo "fedora_release:          ${FEDORA_RELEASE}"
  fi

  REDHAT_RELEASE_DIGIT=""
  if [[ -e "/etc/redhat-release" ]]; then
    REDHAT_RELEASE_DIGIT="$(cat /etc/redhat-release | grep -oE '[0-9]+' | head -n1)"
    echo "REDHAT_RELEASE_DIGIT:    ${REDHAT_RELEASE_DIGIT}"
  elif [[ "$AMAZON1_RELEASE" != "" ]]; then
    echo "AMAZON1_RELEASE:         $AMAZON1_RELEASE"
    REDHAT_RELEASE_DIGIT="6"
    echo "REDHAT_RELEASE_DIGIT:    ${REDHAT_RELEASE_DIGIT}"
  elif [[ "$AMAZON2_RELEASE" != "" ]]; then
    echo "AMAZON2_RELEASE:         $AMAZON2_RELEASE"
    REDHAT_RELEASE_DIGIT="7"
    echo "REDHAT_RELEASE_DIGIT:    ${REDHAT_RELEASE_DIGIT}"
  fi
}


echo "PBase Adminer DB interface"
THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

echo "THISHOSTNAME:            ${THISHOSTNAME}"
echo "THISDOMAINNAME:          ${THISDOMAINNAME}"

## check for htdocs location -

if [[ -d "/var/www/html/${THISDOMAINNAME}/public" ]]; then
  ALT_ROOT="/var/www/html/${THISDOMAINNAME}/public"
elif [[ -d "/var/www/${THISDOMAINNAME}/html" ]]; then
  ALT_ROOT="/var/www/${THISDOMAINNAME}/html"
elif [[ -d "/var/www/html" ]]; then
  ALT_ROOT="/var/www/html"
fi

SUBFOLDER=""
##SUBFOLDER="pbase/"

if [[ -e ${ALT_ROOT}/index.html ]]; then
  echo "Found existing htdocs:   ${ALT_ROOT}/index.html"
  echo "Installing adminer:      ${ALT_ROOT}/${SUBFOLDER}adminer-all.php"
  echo "                         ${ALT_ROOT}/${SUBFOLDER}adminer-mysql.php"
  ADMINER_URL="http://${THISHOSTNAME}/${SUBFOLDER}adminer-mysql.php"

  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-adminer/var-www-html/adminer-all.php  ${ALT_ROOT}/${SUBFOLDER}
  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-adminer/var-www-html/adminer-mysql.php  ${ALT_ROOT}/${SUBFOLDER}
  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-adminer/var-www-html/adminer.css  ${ALT_ROOT}/${SUBFOLDER}
else
  echo "Assume htdocs:           /var/www/html/"
  echo "Installing adminer:      /var/www/html/${SUBFOLDER}adminer-all.php"
  echo "                         /var/www/html/${SUBFOLDER}adminer-mysql.php"
  ADMINER_URL="http://${THISHOSTNAME}/${SUBFOLDER}adminer-mysql.php"

  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-adminer/var-www-html/adminer-all.php  /var/www/html/${SUBFOLDER}
  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-adminer/var-www-html/adminer-mysql.php  /var/www/html/${SUBFOLDER}
  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-adminer/var-www-html/adminer.css  /var/www/html/${SUBFOLDER}
fi

check_linux_version

# Restart httpd service

if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  /sbin/service httpd restart || fail "failed to restart httpd service"
else
  /bin/systemctl daemon-reload
  /bin/systemctl restart httpd || fail "failed to restart httpd service"
fi

echo "Next step, open Adminer with this URL"
#echo "Restart Apache:          systemctl restart httpd"
echo "Adminer URL:             ${ADMINER_URL}"
echo " "


%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-adminer/var-www-html/adminer.css
/usr/local/pbase-data/pbase-adminer/var-www-html/adminer-all.php
/usr/local/pbase-data/pbase-adminer/var-www-html/adminer-mysql.php
