Name: pbase-adminer
Version: 1.0
Release: 2
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

echo "PBase Adminer DB interface"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

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
##SUBFOLDER="pbase"

if [[ -e ${ALT_ROOT}/index.html ]]; then
  echo "Found existing htdocs:   ${ALT_ROOT}/index.html"
  ADMINER_URL="http://${THISHOSTNAME}/${SUBFOLDER}adminer-mysql.php"
  ADMINER_ALL="http://${THISHOSTNAME}/${SUBFOLDER}adminer-all.php"

  tar zxf /usr/local/pbase-data/pbase-adminer/var-www-html/adminer-bundle.tgz -C ${ALT_ROOT}/${SUBFOLDER}/
  ls -l ${ALT_ROOT}/${SUBFOLDER}
else
  echo "Assume htdocs:           /var/www/html/"
  ADMINER_URL="http://${THISHOSTNAME}/${SUBFOLDER}/adminer-mysql.php"
  ADMINER_ALL="http://${THISHOSTNAME}/${SUBFOLDER}/adminer-all.php"

  tar zxf /usr/local/pbase-data/pbase-adminer/var-www-html/adminer-bundle.tgz -C /var/www/html/${SUBFOLDER}/
  ls -l /var/www/html/${SUBFOLDER}
fi

# Restart httpd service

/bin/systemctl daemon-reload
/bin/systemctl restart httpd || fail "failed to restart httpd service"

echo "Next step, open Adminer with this URL"
#echo "Restart Apache:          systemctl restart httpd"
echo "Adminer URL:             ${ADMINER_URL}"
echo "   or                    ${ADMINER_ALL}"
echo " "


%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-adminer/var-www-html/adminer-bundle.tgz
