Name: pbase-website-sample
Version: 1.0
Release: 3
Summary: PBase sample website rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-website-sample-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-website-sample
Requires: pbase-apache

%description
Provides sample website content

%prep
%setup -q

%install
mkdir -p "$RPM_BUILD_ROOT"
cp -R * "$RPM_BUILD_ROOT"

%clean
rm -rf "$RPM_BUILD_ROOT"

%pre

%post
#echo "rpm postinstall $1"


## config may be stored in json file with root-only permissions
##     in the directory: /usr/local/pbase-data/admin-only/module-config.d/

locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_apache.json"
  PBASE_CONFIG_FILENAME="$1"

  PBASE_CONFIG_BASE="/usr/local/pbase-data/admin-only"
  PBASE_ALL_IN_ONE_CONFIG_FILENAME="pbase_module_config.json"
  PBASE_CONFIG_DIR="${PBASE_CONFIG_BASE}/module-config.d"

  PBASE_CONFIG_SEPARATE="${PBASE_CONFIG_DIR}/${PBASE_CONFIG_FILENAME}"
  PBASE_CONFIG_ALLINONE="${PBASE_CONFIG_BASE}/${PBASE_ALL_IN_ONE_CONFIG_FILENAME}"

  #echo "PBASE_CONFIG_SEPARATE:   $PBASE_CONFIG_SEPARATE"
  #echo "PBASE_CONFIG_ALLINONE:   $PBASE_CONFIG_ALLINONE"

  ## check if either file exists, assume SEPARATE as default
  PBASE_CONFIG="$PBASE_CONFIG_SEPARATE"

  if [[ -f "$PBASE_CONFIG_ALLINONE" ]] ; then
    PBASE_CONFIG="$PBASE_CONFIG_ALLINONE"
  fi

  if [[ -f "$PBASE_CONFIG" ]] ; then
    echo "Config file found:       $PBASE_CONFIG"
  else
    echo "Custom config not found: $PBASE_CONFIG"
  fi
}


parseConfig() {
  ## fallback when jq is not installed, use the default in the third param
  HAS_JQ_INSTALLED="$(which jq)"
  #echo "HAS_JQ_INSTALLED:   $HAS_JQ_INSTALLED"

  if [[ -z "$HAS_JQ_INSTALLED" ]] || [[ ! -f "$PBASE_CONFIG" ]] ; then
    ## echo "fallback to default: $3"
    eval "$1"="$3"
    return 1
  fi

  ## use jq to extract a json field named in the second param
  PARSED_VALUE="$(cat $PBASE_CONFIG  |  jq $2)"

  ## use eval to assign that to the variable named in the first param
  eval "$1"="$PARSED_VALUE"
}

echo "PBase-Foundation.com sample website content:"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

## check for default subdomain text file
DEFAULT_SUB_DOMAIN=""
if [[ -e /root/DEFAULT_SUB_DOMAIN.txt ]] ; then
  read -r DEFAULT_SUB_DOMAIN < /root/DEFAULT_SUB_DOMAIN.txt
fi

## look for config file "pbase_apache.json"
PBASE_CONFIG_FILENAME="pbase_apache.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

parseConfig "SERVER_ADMIN_EMAIL" ".pbase_apache.serverAdmin" "${DEFAULT_EMAIL}"
parseConfig "URL_SUBDOMAIN" ".pbase_apache.urlSubDomain" "${DEFAULT_SUB_DOMAIN}"

## FULLDOMAINNAME is the subdomain if declared plus the domain
FULLDOMAINNAME="${THISDOMAINNAME}"

if [[ "${URL_SUBDOMAIN}" != "" ]] ; then
  FULLDOMAINNAME="${URL_SUBDOMAIN}.${THISDOMAINNAME}"
  echo "Using subdomain:         ${FULLDOMAINNAME}"
fi

QT="'"
URL_SUBDOMAIN_QUOTED="${QT}${QT}"

if [[ "${URL_SUBDOMAIN}" != "" ]] ; then
  URL_SUBDOMAIN_QUOTED=${QT}${URL_SUBDOMAIN}${QT}
  echo "Using subdomain:         ${FULLDOMAINNAME}"
fi

echo "URL_SUBDOMAIN:           ${URL_SUBDOMAIN_QUOTED}"

## check for htdocs location
WWW_ROOT="/var/www/html/${FULLDOMAINNAME}/public"

if [[ -d "/var/www/html/${FULLDOMAINNAME}/public" ]]; then
  WWW_ROOT="/var/www/html/${FULLDOMAINNAME}/public"
elif [[ -d "/var/www/${FULLDOMAINNAME}/html" ]]; then
  WWW_ROOT="/var/www/${FULLDOMAINNAME}/html"
elif [[ -d "/var/www/html" ]]; then
  WWW_ROOT="/var/www/html"
fi

echo "WWW_ROOT:                ${WWW_ROOT}"

## set existing 'public' aside with datestamp
cd "${WWW_ROOT}"
cd ..

DATE_SUFFIX="$(date +'%Y-%m-%d_%H-%M')"

echo ""
echo "Setting aside public:    public-PREV-${DATE_SUFFIX}"

mv public "public-PREV-${DATE_SUFFIX}"

mkdir -p ${WWW_ROOT}

tar zxf /usr/local/pbase-data/pbase-website-sample/public.tgz -C /var/www/html/${FULLDOMAINNAME}/

echo "Sample mp3 excerpts:     ${WWW_ROOT}/mp3/"
tar zxf /usr/local/pbase-data/pbase-website-sample/mp3.tgz -C /var/www/

chown -R root:root /var/www/html/${FULLDOMAINNAME}/
chown -R root:root /var/www/mp3/

## links
cd ${WWW_ROOT}/

if [[ -e ${WWW_ROOT}/mp3 ]] ; then
  echo "Already exists:          ${WWW_ROOT}/mp3"
else
  echo "Creating links to media: /var/www/mp3"
  ln -s /var/www/mp3 mp3
  #ln -s /var/www/wav wav

  ## yum
  #ln -s /var/www/yum-repo yum-repo
  #ln -s /var/www/yum-repo/pbase-components/1.0/RPMS/pbase-repo-1.0-3.noarch.rpm pbase-repo.rpm
  #ln -s /var/www/yum-static/ yum-static
fi


if [[ -e ${WWW_ROOT}/.abba ]] ; then
  echo "Already exists:          .abba"
else
  echo "Copying .abba/ and .htaccess resources"
  cd /usr/local/pbase-data/pbase-website-sample/build-deploy/resources/

  tar xf DOT.abba.tar -C ${WWW_ROOT}/
  /bin/cp --no-clobber DOT.htaccess ${WWW_ROOT}/.htaccess
fi

WEBSITE_URL1="http://${FULLDOMAINNAME}"
WEBSITE_URL2="https://${FULLDOMAINNAME}"

echo ""
echo "Website URL:             ${WEBSITE_URL1}"
echo "  if registered in DNS:  ${WEBSITE_URL2}"
echo ""


%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-website-sample/mp3.tgz
/usr/local/pbase-data/pbase-website-sample/public.tgz
/usr/local/pbase-data/pbase-website-sample/build-deploy/resources/DOT.abba.tar
/usr/local/pbase-data/pbase-website-sample/build-deploy/resources/DOT.htaccess
%attr(0600,root,root) /usr/local/pbase-data/pbase-website-sample/build-deploy/build-notes.txt
%attr(0600,root,root) /usr/local/pbase-data/pbase-website-sample/build-deploy/pbase-foundation-build.sh
%attr(0600,root,root) /usr/local/pbase-data/pbase-website-sample/build-deploy/pbase-foundation-deploy.sh
