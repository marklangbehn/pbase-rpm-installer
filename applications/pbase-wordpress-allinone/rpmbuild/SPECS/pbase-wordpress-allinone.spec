Name: pbase-wordpress-allinone
Version: 1.0
Release: 3
Summary: PBase WordPress all-in-one application stack rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-wordpress-allinone-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-wordpress
Requires: pbase-apache, pbase-mysql, pbase-phpmysql-transitive-dep, httpd-tools, wget, dos2unix

## pbase-phpmysql-transitive-dep - has requires for:
## php,php-cli,php-json,php-gd,php-mbstring,php-pdo,php-xml,php-pecl-zip,httpd-tools,wget
## php-mysql    in  EL6 EL7
## php-mysqlnd  in  EL8

%description
PBase WordPress all-in-one application stack

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

## config is stored in json file with root-only permissions
##     in the directory: /usr/local/pbase-data/admin-only/module-config.d/


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

echo "PBase WordPress all-in-one application installer"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

## Let's Encrypt config
PBASE_CONFIG_FILENAME="pbase_lets_encrypt.json"
locateConfigFile "$PBASE_CONFIG_FILENAME"
URL_SUBDOMAIN=""
QT="'"
URL_SUBDOMAIN_QUOTED="${QT}${QT}"
EXECUTE_CERTBOT_CMD="false"
EMAIL_ADDR="yoursysadmin@yourrealmail.com"

if [[ -e "/usr/local/pbase-data/admin-only/module-config.d/pbase_lets_encrypt.json" ]] ; then
  parseConfig "URL_SUBDOMAIN" ".pbase_lets_encrypt.urlSubDomain" ""
  parseConfig "EXECUTE_CERTBOT_CMD" ".pbase_lets_encrypt.executeCertbotCmd" "true"
  parseConfig "EMAIL_ADDR" ".pbase_lets_encrypt.emailAddress" "yoursysadmin@yourrealmail.com"

  URL_SUBDOMAIN_QUOTED=${QT}${URL_SUBDOMAIN}${QT}
  echo "URL_SUBDOMAIN:           ${URL_SUBDOMAIN_QUOTED}"
else
  echo "No subdomain config:     pbase_lets_encrypt.json"
fi

## use a hash of the date as a random-ish string. use head to grab first 8 chars, and next 8 chars
RAND_PW_USER="u$(date +%s | sha256sum | base64 | head -c 8)"
RAND_PW_ROOT="r$(date +%s | sha256sum | base64 | head -c 16 | tail -c 8)"

echo "RAND_PW_USER:            $RAND_PW_USER"
echo "RAND_PW_ROOT:            $RAND_PW_ROOT"


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

HTTP_ONLY="false"
## fetch config value from JSON file
parseConfig "HTTP_ONLY"  ".pbase_wordpress.httpOnly" "false"
parseConfig "WORDPRESS_URI_BASE"  ".pbase_wordpress.wordpressUriBase" ""
parseConfig "CONFIG_SUBDOMAIN_NAME" ".pbase_wordpress.urlSubDomain" ""

URL_SUBDOMAIN=$CONFIG_SUBDOMAIN_NAME

echo "WORDPRESS_URI_BASE:      $WORDPRESS_URI_BASE"
SLASH_WORDPRESS_URI_BASE=""

if [[ "${WORDPRESS_URI_BASE}" != "" ]]; then
  SLASH_WORDPRESS_URI_BASE="/${WORDPRESS_URI_BASE}"
fi

##echo "SLASH_WORDPRESS_URI_BASE: ${SLASH_WORDPRESS_URI_BASE}"
echo ""

## make sure certbot is installed
HAS_CERTBOT_INSTALLED="$(which certbot)"

if [[ -z "${HAS_CERTBOT_INSTALLED}" ]] ; then
  echo "Certbot not installed"
  EXECUTE_CERTBOT_CMD="false"
else
  echo "Certbot is installed     ${HAS_CERTBOT_INSTALLED}"
fi


HAS_APACHE_ROOTDOMAIN_CONF=""
ROOTDOMAIN_HTTP_CONF_FILE="/etc/httpd/conf.d/${THISDOMAINNAME}.conf"

if [[ -e "${ROOTDOMAIN_HTTP_CONF_FILE}" ]] ; then
  echo "Found existing Apache root domain .conf file "
  HAS_APACHE_ROOTDOMAIN_CONF="true"
fi

if [[ -e "/etc/httpd/conf.d/ssl.conf" ]] ; then
  echo "Disabling unused:        /etc/httpd/conf.d/ssl.conf"
  mv "/etc/httpd/conf.d/ssl.conf" "/etc/httpd/conf.d/ssl.conf-DISABLED"
fi

## fetch previously registered domain names
DOMAIN_NAME_LIST=""
SAVE_CMD_DIR="/usr/local/pbase-data/admin-only"

read -r DOMAIN_NAME_LIST < "${SAVE_CMD_DIR}/domain-name-list.txt"

echo "Saved domain names:      ${SAVE_CMD_DIR}/domain-name-list.txt"
echo "Found domain-name-list:  ${DOMAIN_NAME_LIST}"

THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

## FULLDOMAINNAME is the subdomain if declared plus the domain
FULLDOMAINNAME="${THISDOMAINNAME}"

## FIRSTDOMAINNREGISTERED should match the subdirectory under /etc/letsencrypt/live
FIRSTDOMAINNREGISTERED="${FULLDOMAINNAME}"

if [[ ${URL_SUBDOMAIN} == "" ]] || [[ ${URL_SUBDOMAIN} == null ]] ; then
  FULLDOMAINNAME="${THISDOMAINNAME}"
  echo "Using root domain:       ${FULLDOMAINNAME}"
else
  FULLDOMAINNAME="${URL_SUBDOMAIN}.${THISDOMAINNAME}"
  echo "Using subdomain:         ${FULLDOMAINNAME}"
fi


DOMAIN_NAME_LIST_NEW=""
DOMAIN_NAME_PARAM=""

echo "Found DOMAIN_NAME_LIST:  ${DOMAIN_NAME_LIST}"

if [[ "${DOMAIN_NAME_LIST}" == "" ]] ; then
  echo "Starting from empty domain-name-list.txt, adding ${FULLDOMAINNAME}"
  DOMAIN_NAME_LIST_NEW="${FULLDOMAINNAME}"
  DOMAIN_NAME_PARAM="${FULLDOMAINNAME}"
else
    ## use cut to grab first name from comma delimited list
    FIRSTDOMAINNREGISTERED=$(cut -f1 -d "," ${SAVE_CMD_DIR}/domain-name-list.txt)
    echo "FIRSTDOMAINNREGISTERED:  ${FIRSTDOMAINNREGISTERED}"

  if [[ "${DOMAIN_NAME_LIST}" == *"${FULLDOMAINNAME}"* ]]; then
    echo "Already has ${FULLDOMAINNAME}"
    DOMAIN_NAME_LIST_NEW="${DOMAIN_NAME_LIST}"
    DOMAIN_NAME_PARAM="${DOMAIN_NAME_LIST}"
  else
    echo "Adding ${FULLDOMAINNAME}"
    DOMAIN_NAME_LIST_NEW="${DOMAIN_NAME_LIST},${FULLDOMAINNAME}"
    DOMAIN_NAME_PARAM="${DOMAIN_NAME_LIST},${FULLDOMAINNAME} --expand"
  fi
fi

echo ""
echo "${DOMAIN_NAME_LIST_NEW}" > ${SAVE_CMD_DIR}/domain-name-list.txt
echo "Saved domain names:      ${SAVE_CMD_DIR}/domain-name-list.txt"
echo "                         ${DOMAIN_NAME_LIST_NEW}"
echo ""

DOMAIN_NAME_LIST_HAS_WWW=$(grep www ${SAVE_CMD_DIR}/domain-name-list.txt)
#echo "Domain list has WWW:     ${DOMAIN_NAME_LIST_HAS_WWW}"

## check for htdocs location
WWW_ROOT="/var/www/html/${FULLDOMAINNAME}/public"

#WWW_ROOT="/var/www/html/${FULLDOMAINNAME}/public"
#if [[ -d "/var/www/html/${FULLDOMAINNAME}/public" ]]; then
#  WWW_ROOT="/var/www/html/${FULLDOMAINNAME}/public"
#elif [[ -d "/var/www/${FULLDOMAINNAME}/html" ]]; then
#  WWW_ROOT="/var/www/${FULLDOMAINNAME}/html"
#elif [[ -d "/var/www/html" ]]; then
#  WWW_ROOT="/var/www/html/${FULLDOMAINNAME}"
#fi

## check if already installed
#if [[ -d "$WWW_ROOT/wp-config.php/" ]]; then
#  echo "$WWW_ROOT/wp-config.php already exists - exiting"
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
  echo "URI Base is empty, Wordpress will be website root"
  if [[ -d "${WWW_ROOT}" ]] ; then
    mv "${WWW_ROOT}" ${WWW_ROOT}-$(date +"%Y-%m-%d_%H-%M-%S")
  fi

  echo "Creating Wordpress home: ${WWW_ROOT}"
  mkdir -p "${WWW_ROOT}"

  cd "${DOWNLOADED_DIR}/wordpress"
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


## VirtualHost

ROOT_VHOST_CONF_FILE="/etc/httpd/conf.d/${THISDOMAINNAME}.conf"
VHOST_CONF_FILE="/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"
echo "Wordpress VirtualHost:   ${VHOST_CONF_FILE}"

if [[ -e "${VHOST_CONF_FILE}" ]] ; then
  echo "Disabling existing VirtualHost"
  mv "${VHOST_CONF_FILE}" "${VHOST_CONF_FILE}-DISABLED"
fi

if [[ ${URL_SUBDOMAIN} == "" ]] || [[ ${URL_SUBDOMAIN} == null ]] ; then
  echo "Using root domain:       /etc/httpd/conf/httpd.conf"
  /bin/cp --no-clobber /usr/local/pbase-data/pbase-wordpress-allinone/etc-httpd-confd/wordpress-rootdomain.conf ${ROOT_VHOST_CONF_FILE}

  ## may also enable www alias
  sed -i "s/www.example.com/www.${THISDOMAINNAME}/" "${ROOT_VHOST_CONF_FILE}"
  ##sed -i "s/example.com/${THISDOMAINNAME}/" "${ROOT_VHOST_CONF_FILE}"

  if [[ "${DOMAIN_NAME_LIST_HAS_WWW}" != "" ]] ; then
    echo "Enabling:                ServerAlias www.${THISDOMAINNAME}"
    sed -i "s/#ServerAlias/ServerAlias/" "${ROOT_VHOST_CONF_FILE}"
  fi

else
  echo "Using subdomain:         ${FULLDOMAINNAME}"
  /bin/cp --no-clobber /usr/local/pbase-data/pbase-wordpress-allinone/etc-httpd-confd/wordpress-subdomain.conf ${VHOST_CONF_FILE}

  ## modify root VirtuaHost to have * instead of domainname
  #if [[ -e "${ROOT_VHOST_CONF_FILE}" ]] ; then
  #  echo "Setting VirtualHost *:   ${ROOT_VHOST_CONF_FILE}"
  #  sed -i "s/VirtualHost ${THISDOMAINNAME}/VirtualHost */" "${ROOT_VHOST_CONF_FILE}"
  #fi

  ## handle WP file with CR/LF line endings
  dos2unix "${WP_CONFIG_PHP}"

  echo "Set https WP_SITEURL:    ${WP_CONFIG_PHP}"

  HTTP_OR_HTTPS="https"
  if [[ ${HTTP_ONLY} == "true" ]] ; then
    echo "Setting httpOnly"
    HTTP_OR_HTTPS="http"
  fi

  HTTP_FULLDOMAINNAME_QUOTED="${QT}${HTTP_OR_HTTPS}://${FULLDOMAINNAME}${QT}"
  echo "Adding subdomain WP_HOME and WP_SITEURL to wp-config.php"
  echo ""  >>  "${WP_CONFIG_PHP}"
  echo "define('WP_HOME', ${HTTP_FULLDOMAINNAME_QUOTED});"  >>  "${WP_CONFIG_PHP}"
  echo "define('WP_SITEURL', ${HTTP_FULLDOMAINNAME_QUOTED});"  >>  "${WP_CONFIG_PHP}"
  echo ""  >>  "${WP_CONFIG_PHP}"
fi

echo "Setting domain:          ${FULLDOMAINNAME}"
sed -i "s/subdomain.example.com/${FULLDOMAINNAME}/" "${VHOST_CONF_FILE}"
sed -i "s/yoursysadmin@yourrealmail.com/${EMAIL_ADDR}/" "${VHOST_CONF_FILE}"

echo "Log directory:           /var/log/httpd/${FULLDOMAINNAME}/"
mkdir -p "/var/log/httpd/${FULLDOMAINNAME}/"


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
  if [[ -e "/etc/php-fpm-7.2.d/www.conf" ]]; then
    echo "Updating:                /etc/php-fpm-7.2.d/www.conf"
    sed -i "s/apache,nginx/apache/" "/etc/php-fpm-7.2.d/www.conf"
  fi

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
  /bin/systemctl restart httpd || fail "failed to restart httpd service"
fi


if [[ -z "${HAS_CERTBOT_INSTALLED}" ]] ; then
  echo "Certbot not installed"
else
  ## LETS ENCRYPT - HTTPS CERTIFICATE
  echo ""
  CERTBOT_CMD="certbot --apache --agree-tos --email ${EMAIL_ADDR} -n -d ${DOMAIN_NAME_PARAM}"

  ## save command line in file
  echo "Saving command line:     ${SAVE_CMD_DIR}/certbot-cmd.sh"
  echo ${CERTBOT_CMD} > ${SAVE_CMD_DIR}/certbot-cmd.sh

  if [[ $EXECUTE_CERTBOT_CMD == "true" ]] ; then
    echo "Executing:               ${CERTBOT_CMD}"
    echo ""
    eval "${CERTBOT_CMD}"
  else
    echo "Skipping execute:        EXECUTE_CERTBOT_CMD=false"
    echo "                         ${CERTBOT_CMD}"
  fi
fi


echo "WordPress web application is running."
echo "Next step - required - Open this URL to complete the install."
echo "if locally installed"
echo "                         http://localhost${SLASH_WORDPRESS_URI_BASE}"
echo "if hostname is accessible"
echo "                         http://${FULLDOMAINNAME}${SLASH_WORDPRESS_URI_BASE}"
echo "or if your domain is registered in DNS and has HTTPS enabled"
echo "                         https://${FULLDOMAINNAME}${SLASH_WORDPRESS_URI_BASE}"
echo ""

%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-wordpress-allinone/etc-httpd-confd/wordpress-rootdomain.conf
/usr/local/pbase-data/pbase-wordpress-allinone/etc-httpd-confd/wordpress-subdomain.conf
