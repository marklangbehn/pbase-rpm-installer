Name: pbase-nextcloud
Version: 1.0
Release: 0
Summary: PBase NextCloud service rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-nextcloud-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-nextcloud
Requires: pbase-phpmysql-transitive-dep, pbase-apache, unzip, wget

## pbase-phpmysql-transitive-dep - has requires for:
## php,php-cli,php-json,php-gd,php-mbstring,php-pdo,php-xml,php-pecl-zip,httpd-tools,wget
## php-mysqlnd  in  EL6
## php-mysql    in  EL7
## php-mysqlnd  in  EL8 and Fedora

%description
PBase Nextcloud service

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

append_bashrc_alias() {
  if [ -z "$1" ]  ||  [ -z "$2" ]; then
    echo "Both params must be passed to postinstall.append_bashrc_alias()"
    exit 1
  fi

  EXISTING_ALIAS=$(grep $1 /root/.bashrc)
  if [[ "$EXISTING_ALIAS" == "" ]]; then
    echo "Adding shell alias:  $1"
    echo "alias $1='$2'"  >>  /root/.bashrc
  else
    echo "Already has shell alias '$1' in: /root/.bashrc"
  fi
}

copy_if_not_exists() {
  if [ -z "$1" ]  ||  [ -z "$2" ]  ||  [ -z "$3" ]; then
    echo "All 3 params must be passed to copy_if_not_exists function"
    exit 1
  fi

  FILENAME="$1"
  SOURCE_DIR="$2"
  DEST_DIR="$3"

  SOURCE_FILE_PATH=$SOURCE_DIR/$FILENAME
  DEST_FILE_PATH=$DEST_DIR/$FILENAME

  if [[ -f "$DEST_FILE_PATH" ]] ; then
    echo "Already exists:          $DEST_FILE_PATH"
    return 0
  else
    echo "Copying file:            $DEST_FILE_PATH"
    /bin/cp -rf --no-clobber $SOURCE_FILE_PATH  $DEST_DIR
    return 1
  fi
}


echo "PBase NextCloud installer"

## config is stored in json file with root-only permissions
## it can be one of two places:
##     /usr/local/pbase-data/admin-only/pbase_module_config.json
## or
##     /usr/local/pbase-data/admin-only/module-config.d/pbase_nextcloud.json


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_nextcloud.json"
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


check_linux_version
echo ""

## look for either separate config file "pbase_gitea.json" or all-in-one file: "pbase_module_config.json"
PBASE_CONFIG_FILENAME="pbase_nextcloud.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "HTTP_PORT" ".pbase_nextcloud.httpPort" "3000"
parseConfig "ADD_APACHE_PROXY" ".pbase_nextcloud.addApacheProxy" "true"

#echo "HTTP_PORT:               $HTTP_PORT"
#echo "ADD_APACHE_PROXY:        $ADD_APACHE_PROXY"


THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

## check for htdocs location
WWW_ROOT="/var/www/html"

if [[ -d "/var/www/html/${THISDOMAINNAME}/public" ]]; then
  WWW_ROOT="/var/www/html/${THISDOMAINNAME}/public"
elif [[ -d "/var/www/${THISDOMAINNAME}/html" ]]; then
  WWW_ROOT="/var/www/${THISDOMAINNAME}/html"
elif [[ -d "/var/www/html" ]]; then
  WWW_ROOT="/var/www/html"
fi

## check if already installed
if [[ -d "$WWW_ROOT/nextcloud/" ]]; then
  echo "$WWW_ROOT/nextcloud/ directory already exists - exiting"
  exit 0
fi

## prevent .htaccess file from causing problems for wordpress - if found rename it to DOT.htaccess
if [[ -e "${WWW_ROOT}/.htaccess" ]] ; then
  echo "Found .htaccess:         ${WWW_ROOT}/.htaccess"
  echo "Renaming to:             DOT.htaccess"

  mv "${WWW_ROOT}/.htaccess" "${WWW_ROOT}/DOT.htaccess"
fi

echo "Downloading NextCloud server binary from download.nextcloud.com"

mkdir -p /usr/local/pbase-data/pbase-nextcloud
cd /usr/local/pbase-data/pbase-nextcloud

wget -q https://download.nextcloud.com/server/releases/latest.zip

echo "Downloaded file from download.nextcloud.com:"

ls -lh latest.zip

VAR_WWW_ROOT="/var/www"

echo "Unzipping to:            $VAR_WWW_ROOT"
unzip -q latest.zip -d "$VAR_WWW_ROOT"

mkdir $VAR_WWW_ROOT/nextcloud/data
chown -R apache:apache $VAR_WWW_ROOT/nextcloud/*

echo "Apache alias config:     /etc/httpd/conf.d/nextcloud.conf"
/bin/cp --no-clobber /usr/local/pbase-data/pbase-nextcloud/etc-httpd-confd/nextcloud.conf /etc/httpd/conf.d/


## adjust php-fpm owners list
PHP_FPM_CONF="/etc/php-fpm-7.2.d/www.conf"

if [[ -e "$PHP_FPM_CONF" ]]; then
  NEEDS_OWNERS_FIX=$(grep "^listen\.acl_users = apache,nginx" "$PHP_FPM_CONF")

  if [[ "$NEEDS_OWNERS_FIX" != "" ]]; then
    echo "Adjust owners list:      $PHP_FPM_CONF"
    sed -i "s/^listen\.acl_users = apache,nginx/listen.acl_users = apache/" "$PHP_FPM_CONF"
  else
    echo "Leaving unchanged:       $PHP_FPM_CONF"
  fi
fi

## on Amzn1 remove the temporary yum repo file added by preconfig
if [[ -e "/etc/yum.repos.d/amzn2extra-php72.repo" ]]; then
  echo "Removing:                /etc/yum.repos.d/amzn2extra-php72.repo"
  /bin/rm -f /etc/yum.repos.d/amzn2extra-php72.repo

  if [[ "$AMAZON1_RELEASE" != "" ]]; then
    echo "To enable PHP updates run this command:"
    echo "                         amazon-linux-extras install php7.2"
  fi
fi


echo "Restarting php-fpm and httpd"

if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  /sbin/chkconfig php-fpm --level 345 on || fail "chkconfig failed to enable php-fpm service"
  /sbin/service php-fpm restart

  /sbin/service httpd restart || fail "failed to restart httpd service"
else
  /bin/systemctl daemon-reload

  /bin/systemctl enable php-fpm
  /bin/systemctl restart php-fpm

  /bin/systemctl restart httpd || fail "failed to restart httpd service"
fi

echo "Default PBase module configuration directory:"
echo "                        /usr/local/pbase-data/admin-only/module-config.d/"

echo "NextCloud web application is running."
echo "Next step - Open this URL to complete the install:"
echo "if locally installed"
echo "                         http://localhost/nextcloud"
echo "if hostname is accessible"
echo "                         http://${THISHOSTNAME}/nextcloud"
echo "or if your domain is registered in DNS"
echo "                         http://${THISDOMAINNAME}/nextcloud"
echo ""


%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-nextcloud/etc-httpd-confd/nextcloud.conf
/usr/local/pbase-data/pbase-nextcloud/etc-httpd-confd/nextcloud-vhost.conf