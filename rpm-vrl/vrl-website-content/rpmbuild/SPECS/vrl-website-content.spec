Name: vrl-website-content
Version: 1.0
Release: 0
Summary: PBase VirtualRecordLabel.net sample website rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: vrl-website-content-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: vrl-website-content
Requires: pbase-apache

%description
Provides virtualrecordlabel.net sample website content

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

THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"


echo "VirtualRecordLabel.net website content:"
echo "                         /var/www/html/${THISDOMAINNAME}/public/"
/bin/rm -rf /var/www/html/${THISDOMAINNAME}/public

tar zxf /usr/local/pbase-data/vrl-website-content/public.tgz -C /var/www/html/${THISDOMAINNAME}/

echo "Sample mp3 excerpts:     /var/www/html/${THISDOMAINNAME}/public/mp3/"
tar zxf /usr/local/pbase-data/vrl-website-content/mp3.tgz -C /var/www/

chown -R root:root /var/www/html/${THISDOMAINNAME}/
chown -R root:root /var/www/mp3/

## links
cd /var/www/html/${THISDOMAINNAME}/public/

if [[ -e /var/www/html/${THISDOMAINNAME}/public/mp3 ]] ; then
  echo "Already exists:          /var/www/html/${THISDOMAINNAME}/public/mp3"
else
  echo "Creating links to media: /var/www/mp3"
  ln -s /var/www/mp3 mp3
  #ln -s /var/www/mark mark
  #ln -s /var/www/wav wav

  ## yum
  #ln -s /var/www/yum-repo yum-repo
  #ln -s /var/www/yum-repo/pbase-components/1.0/RPMS/pbase-preconfig-1.0-0.noarch.rpm pbase-repo.rpm
  #ln -s /var/www/yum-static/ yum-static
fi


if [[ -e /var/www/html/${THISDOMAINNAME}/public/.abba ]] ; then
  echo "Already exists:          .abba"
else
  echo "Copying .abba/ and .htaccess resources"
  cd /usr/local/pbase-data/vrl-website-content/build-deploy/resources/

  tar xf DOT.abba.tar -C /var/www/html/${THISDOMAINNAME}/public/
  /bin/cp --no-clobber DOT.htaccess /var/www/html/${THISDOMAINNAME}/public/.htaccess
fi

WEBSITE_URL1="http://${THISHOSTNAME}"
WEBSITE_URL2="http://${THISDOMAINNAME}"

echo ""
echo "Website URL:             ${WEBSITE_URL1}"
echo "  if registered in DNS:  ${WEBSITE_URL2}"
echo ""


%files
%defattr(-,root,root,-)
/usr/local/pbase-data/vrl-website-content/mp3.tgz
/usr/local/pbase-data/vrl-website-content/public.tgz
/usr/local/pbase-data/vrl-website-content/build-deploy/resources/DOT.abba.tar
/usr/local/pbase-data/vrl-website-content/build-deploy/resources/DOT.htaccess
/usr/local/pbase-data/vrl-website-content/build-deploy/build-notes.txt
/usr/local/pbase-data/vrl-website-content/build-deploy/virtualrecordlabel-build.sh
/usr/local/pbase-data/vrl-website-content/build-deploy/virtualrecordlabel-deploy.sh
