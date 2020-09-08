Name: pbase-wordpress
Version: 1.0
Release: 0
Summary: PBase WordPress service rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-wordpress
Requires: pbase-phpmysql-transitive-dep,httpd-tools,wget

## pbase-phpmysql-transitive-dep - has requires for:
## php,php-cli,php-json,php-gd,php-mbstring,php-pdo,php-xml,php-pecl-zip,httpd-tools,wget
## php-mysql    in  EL6 EL7
## php-mysqlnd  in  EL8

%description
PBase WordPress web application

%prep

%install

%clean

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


echo "PBase WordPress installer"

## use a hash of the date as a random-ish string. use head to grab first 8 chars, and next 8 chars
RAND_PW_USER="u$(date +%s | sha256sum | base64 | head -c 8)"
RAND_PW_ROOT="r$(date +%s | sha256sum | base64 | head -c 16 | tail -c 8)"

echo "RAND_PW_USER:            $RAND_PW_USER"
echo "RAND_PW_ROOT:            $RAND_PW_ROOT"

## config is stored in json file with root-only permsissions
## it can be one of two places:
##     /usr/local/pbase-data/admin-only/pbase_module_config.json
## or
##     /usr/local/pbase-data/admin-only/module-config.d/pbase_wordpress.json


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_wordpress.json"
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

## MYSQL
PBASE_CONFIG_FILENAME="pbase_mysql.json"
locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file

parseConfig "CONFIG_DB_HOSTNAME" ".pbase_mysql[0].default.hostName" "localhost"
parseConfig "CONFIG_DB_ROOTPSWD" ".pbase_mysql[0].default.rootPassword" $RAND_PW_ROOT
parseConfig "CONFIG_DB_PORT"     ".pbase_mysql[0].default.port" "3306"
parseConfig "CONFIG_DB_CHARSET"  ".pbase_mysql[0].default.characterSet" "utf8mb4"

parseConfig "CONFIG_DB_STARTSVC" ".pbase_mysql[0].default.startService" "true"
parseConfig "CONFIG_DB_INSTALL"  ".pbase_mysql[0].default.install" "true"

parseConfig "CONFIG_DB_NAME"     ".pbase_mysql[0].default.database[0].name" "wordpress"
parseConfig "CONFIG_DB_USER"     ".pbase_mysql[0].default.database[0].user" "admin"
parseConfig "CONFIG_DB_PSWD"     ".pbase_mysql[0].default.database[0].password" $RAND_PW_USER

echo "CONFIG_DB_HOSTNAME:      $CONFIG_DB_HOSTNAME"
echo "CONFIG_DB_ROOTPSWD:      $CONFIG_DB_ROOTPSWD"
echo "CONFIG_DB_PORT:          $CONFIG_DB_PORT"
echo "CONFIG_DB_CHARSET:       $CONFIG_DB_CHARSET"

echo "CONFIG_DB_STARTSVC:      $CONFIG_DB_STARTSVC"
echo "CONFIG_DB_INSTALL:       $CONFIG_DB_INSTALL"
echo ""
echo "CONFIG_DB_NAME:          $CONFIG_DB_NAME"
echo "CONFIG_DB_USER:          $CONFIG_DB_USER"
echo "CONFIG_DB_PSWD:          $CONFIG_DB_PSWD"

echo ""

## WORDPRESS
PBASE_CONFIG_FILENAME="pbase_wordpress.json"
locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "WORDPRESS_URI_BASE"  ".pbase_wordpress.wordpressUriBase" "wordpress"

echo "WORDPRESS_URI_BASE:      $WORDPRESS_URI_BASE"
SLASH_WORDPRESS_URI_BASE="/${WORDPRESS_URI_BASE}"
##echo "SLASH_WORDPRESS_URI_BASE: ${SLASH_WORDPRESS_URI_BASE}"
echo ""

THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

## check for htdocs location
WWW_ROOT="/var/www/html/${THISDOMAINNAME}/public"

if [[ -d "/var/www/html/${THISDOMAINNAME}/public" ]]; then
  WWW_ROOT="/var/www/html/${THISDOMAINNAME}/public"
elif [[ -d "/var/www/${THISDOMAINNAME}/html" ]]; then
  WWW_ROOT="/var/www/${THISDOMAINNAME}/html"
elif [[ -d "/var/www/html" ]]; then
  WWW_ROOT="/var/www/html"
fi

## check if already installed
#if [[ -d "$WWW_ROOT/wordpress/" ]]; then
#  echo "$WWW_ROOT/wordpress/ directory already exists - exiting"
#  exit 0
#fi

echo "Downloading from download.wordpress.com"

DOWNLOADED_DIR="/usr/local/pbase-data/pbase-wordpress/downloaded"
mkdir -p "${DOWNLOADED_DIR}"

echo "Download directory:      ${DOWNLOADED_DIR}"

cd "${DOWNLOADED_DIR}"
/bin/rm -rf *

echo "Executing:               wget -q https://wordpress.org/latest.tar.gz"

wget -q https://wordpress.org/latest.tar.gz

echo "Downloaded file from download.wordpress.org:"
chown root:root latest.tar.gz
ls -lh latest.tar.gz

echo "Unzipping to:            ${WWW_ROOT}"
tar zxf latest.tar.gz

ls -lh

if [[ $WORDPRESS_URI_BASE == "" ]] ; then
  echo "URI Base is empty, moving to web root"
  cd wordpress
  mv * "${WWW_ROOT}/"
else
  echo "URI Base is:             $WORDPRESS_URI_BASE"
  if [[ $WORDPRESS_URI_BASE != "wordpress" ]] ; then
    mv wordpress $WORDPRESS_URI_BASE
  fi
  mv $WORDPRESS_URI_BASE "${WWW_ROOT}/"
fi

## prevent .htaccess file from causing problems for wordpress - if found rename it to DOT.htaccess
if [[ -e "${WWW_ROOT}/.htaccess" ]] ; then
  echo "Found .htaccess:         ${WWW_ROOT}/.htaccess"
  echo "Renaming to:             DOT.htaccess"

  mv "${WWW_ROOT}/.htaccess" "${WWW_ROOT}/DOT.htaccess"
fi


mkdir -p "${WWW_ROOT}${SLASH_WORDPRESS_URI_BASE}/wp-content/uploads"

#mkdir $WWW_ROOT/${WORDPRESS_URI_BASE}/data

cd "${WWW_ROOT}${SLASH_WORDPRESS_URI_BASE}"

cp wp-config-sample.php wp-config.php

echo "Permissions:             chown -R apache:apache $WWW_ROOT"
chown -R apache:apache $WWW_ROOT


WP_CONFIG_PHP="${WWW_ROOT}${SLASH_WORDPRESS_URI_BASE}/wp-config.php"
echo "Setting wp-config.php:   ${WP_CONFIG_PHP}"

## WP default names and passwords in wp-config.php script to be replaced
TMPL_DB_NAME="database_name_here"
TMPL_APPUSER_NAME="username_here"
TMPL_APPUSER_PSWD="password_here"

sed -i "s/$TMPL_DB_NAME/$CONFIG_DB_NAME/" "${WP_CONFIG_PHP}"
sed -i "s/$TMPL_APPUSER_NAME/$CONFIG_DB_USER/" "${WP_CONFIG_PHP}"
sed -i "s/$TMPL_APPUSER_PSWD/$CONFIG_DB_PSWD/" "${WP_CONFIG_PHP}"


## on Amzn1 remove the temporary yum repo file added by preconfig
if [[ -e "/etc/yum.repos.d/amzn2extra-php72.repo" ]]; then
  echo "Removing:                /etc/yum.repos.d/amzn2extra-php72.repo"
  /bin/rm -f /etc/yum.repos.d/amzn2extra-php72.repo

  if [[ "$AMAZON1_RELEASE" != "" ]]; then
    echo "To enable PHP updates run this command:"
    echo "                         amazon-linux-extras install php7.2"
  fi
fi

echo "Restarting php-fpm"

if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  /sbin/chkconfig php-fpm --level 345 on || fail "chkconfig failed to enable php-fpm service"
  /sbin/service php-fpm restart
else
  /bin/systemctl daemon-reload

  /bin/systemctl enable php-fpm
  /bin/systemctl restart php-fpm
fi

echo "Restarting httpd"

if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  /sbin/service httpd restart || fail "failed to restart httpd service"
else
  /bin/systemctl daemon-reload
  /bin/systemctl restart httpd || fail "failed to restart httpd service"
fi


echo "WordPress web application is running."
echo "Next step - Open this URL to complete the install:"
echo "if locally installed"
echo "                         http://localhost${SLASH_WORDPRESS_URI_BASE}"
#echo "                         http://localhost"
echo "if hostname is accessible"
echo "                         http://${THISHOSTNAME}${SLASH_WORDPRESS_URI_BASE}"
#echo "                         http://${THISHOSTNAME}"
echo "or if your domain is registered in DNS"
echo "                         http://${THISDOMAINNAME}${SLASH_WORDPRESS_URI_BASE}"
#echo "                         http://${THISDOMAINNAME}"
echo ""


%files
