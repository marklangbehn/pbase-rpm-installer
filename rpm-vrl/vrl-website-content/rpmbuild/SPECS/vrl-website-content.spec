Name: vrl-website-content
Version: 1.0
Release: 3
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

echo "VirtualRecordLabel.net website content:"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

## check for default subdomain text file
DEFAULT_SUB_DOMAIN=""
CUSTOM_DOMAINNAME=""
CUSTOM_WWW_DOMAINNAME=""

if [[ -e /root/DEFAULT_SUB_DOMAIN.txt ]] ; then
  read -r DEFAULT_SUB_DOMAIN < /root/DEFAULT_SUB_DOMAIN.txt
fi

if [[ -e /root/CUSTOM_DOMAINNAME.txt ]] ; then
  read -r CUSTOM_DOMAINNAME < /root/CUSTOM_DOMAINNAME.txt
fi

if [[ -e /root/CUSTOM_WWW_DOMAINNAME.txt ]] ; then
  read -r CUSTOM_WWW_DOMAINNAME < /root/CUSTOM_WWW_DOMAINNAME.txt
fi

## look for config file "pbase_apache.json"
PBASE_CONFIG_FILENAME="pbase_apache.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

parseConfig "SERVER_ADMIN_EMAIL" ".pbase_apache.serverAdmin" "${DEFAULT_EMAIL}"
parseConfig "URL_SUBDOMAIN" ".pbase_apache.urlSubDomain" "${DEFAULT_SUB_DOMAIN}"

## FULLDOMAINNAME is the subdomain if declared plus the domain
FULLDOMAINNAME="${THISDOMAINNAME}"

## when the hostname of the server is not same as name of website it must be overridden with CUSTOM_DOMAINNAME
if [[ "${CUSTOM_DOMAINNAME}" != "" ]] ; then
  THISDOMAINNAME="${CUSTOM_DOMAINNAME}"
  echo "Using CUSTOM_DOMAINNAME: ${THISDOMAINNAME}"
fi


if [[ "${URL_SUBDOMAIN}" != "" ]] ; then
  FULLDOMAINNAME="${URL_SUBDOMAIN}.${THISDOMAINNAME}"
  echo "Using subdomain:         ${FULLDOMAINNAME}"
fi

if [[ "${CUSTOM_DOMAINNAME}" != "" ]] ; then
  CUSTOM_DIR="/var/www/html/${FULLDOMAINNAME}/public"
  echo "Custom html directory:   ${CUSTOM_DIR}"
  mkdir -p "${CUSTOM_DIR}"

  ## /usr/local/pbase-data/admin-only/domain-name-list.txt
  ## /usr/local/pbase-data/admin-only/certbot-cmd.sh

  ADD_DOMAINS_FOR_CERTBOT="${CUSTOM_DOMAINNAME}"

  if [[ "${CUSTOM_WWW_DOMAINNAME}" != "" ]] ; then
    echo "CUSTOM_WWW_DOMAINNAME:   ${CUSTOM_WWW_DOMAINNAME}"
    ADD_DOMAINS_FOR_CERTBOT="${ADD_DOMAINS_FOR_CERTBOT},www.${CUSTOM_WWW_DOMAINNAME}"
  fi

  SAVE_CMD_DIR="/usr/local/pbase-data/admin-only"
  if [[ -e "${SAVE_CMD_DIR}/certbot-cmd.sh" ]] ; then

    read -r DOMAIN_NAME_LIST < "${SAVE_CMD_DIR}/domain-name-list.txt"

    echo "${DOMAIN_NAME_LIST_NEW}" > ${SAVE_CMD_DIR}/domain-name-list.txt
    echo "Saved domain names:      ${SAVE_CMD_DIR}/domain-name-list.txt"
    echo "                         ${DOMAIN_NAME_LIST_NEW}"
  fi

  if [[ -e "${SAVE_CMD_DIR}/domain-name-list.txt" ]] ; then
      read -r DOMAIN_NAME_LIST < "${SAVE_CMD_DIR}/domain-name-list.txt"
  fi

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

tar zxf /usr/local/pbase-data/vrl-website-content/public.tgz -C /var/www/html/${FULLDOMAINNAME}/

echo "Sample mp3 excerpts:     ${WWW_ROOT}/mp3/"
tar zxf /usr/local/pbase-data/vrl-website-content/mp3.tgz -C /var/www/

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
  cd /usr/local/pbase-data/vrl-website-content/build-deploy/resources/

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
/usr/local/pbase-data/vrl-website-content/mp3.tgz
/usr/local/pbase-data/vrl-website-content/public.tgz
/usr/local/pbase-data/vrl-website-content/build-deploy/resources/DOT.abba.tar
/usr/local/pbase-data/vrl-website-content/build-deploy/resources/DOT.htaccess
/usr/local/pbase-data/vrl-website-content/build-deploy/build-notes.txt
/usr/local/pbase-data/vrl-website-content/build-deploy/virtualrecordlabel-build.sh
/usr/local/pbase-data/vrl-website-content/build-deploy/virtualrecordlabel-deploy.sh
