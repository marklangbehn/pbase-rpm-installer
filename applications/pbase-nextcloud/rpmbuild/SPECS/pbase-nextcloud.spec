Name: pbase-nextcloud
Version: 1.0
Release: 6
Summary: PBase NextCloud service rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-nextcloud-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-nextcloud
Requires: pbase-lets-encrypt-transitive-dep, pbase-phpmysql-transitive-dep, pbase-apache, unzip, wget, pbase-epel, ImageMagick, ImageMagick-devel, php-devel, php-pear, gcc, make

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
  AMAZON20XX_RELEASE=""
  if [[ -e "/etc/system-release" ]]; then
    SYSTEM_RELEASE="$(cat /etc/system-release)"
    AMAZON1_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux AMI')"
    AMAZON2_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux release 2 ')"
    AMAZON20XX_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux release 20')"
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
  elif [[ "$AMAZON20XX_RELEASE" != "" ]]; then
    echo "AMAZON20XX_RELEASE:      $AMAZON20XX_RELEASE"
    REDHAT_RELEASE_DIGIT="9"
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

commentOutFile() {
  ## disable config file in directory $1 named $2
  echo "Checking for:            ${1}/${2}"

  if [[ -e "${1}/${2}" ]] ; then
    DATE_SUFFIX="$(date +'%Y-%m-%d_%H-%M')"

    ##echo "Backup:                  ${1}/${2}-PREV-${DATE_SUFFIX}"
    cp -p "${1}/${2}" "${1}/${2}-PREV-${DATE_SUFFIX}"

    ## comment out with a '#' in front of all lines
    echo "Commenting out contents: ${2}"
    sed -i 's/^\([^#].*\)/# \1/g' "${1}/${2}"
  fi
}

echo "PBase NextCloud installer"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

check_linux_version
echo ""
echo "Default PBase module configuration directory:"
echo "                         /usr/local/pbase-data/admin-only/module-config.d/"

## look for config file "pbase_nextcloud.json"
PBASE_CONFIG_FILENAME="pbase_nextcloud.json"
locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "DATABASE" ".pbase_nextcloud.database" ""
parseConfig "CONFIG_URLSUBPATH" ".pbase_nextcloud.urlSubPath" ""
parseConfig "URL_SUBDOMAIN" ".pbase_nextcloud.urlSubDomain" "nextcloud"

echo "DATABASE:                $DATABASE"
echo "CONFIG_URLSUBPATH:       $CONFIG_URLSUBPATH"
echo "URL_SUBDOMAIN:           $URL_SUBDOMAIN"

SLASH_NEXTCLOUD_URLSUBPATH=""

if [[ "${CONFIG_URLSUBPATH}" != "" ]]; then
  SLASH_NEXTCLOUD_URLSUBPATH="/${CONFIG_URLSUBPATH}"
fi

echo "SLASH_NEXTCLOUD_URLSUBPATH: ${SLASH_NEXTCLOUD_URLSUBPATH}"

## look for config file "pbase_apache.json"
PBASE_CONFIG_FILENAME="pbase_apache.json"
locateConfigFile "$PBASE_CONFIG_FILENAME"
parseConfig "ENABLE_CHECK_FOR_WWW" ".pbase_apache.enableCheckForWww" "true"

echo "ENABLE_CHECK_FOR_WWW:    $ENABLE_CHECK_FOR_WWW"


PBASE_CONFIG_FILENAME="pbase_lets_encrypt.json"
locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "CONFIG_ENABLE_AUTORENEW" ".pbase_lets_encrypt.enableAutoRenew" "true"
parseConfig "EXECUTE_CERTBOT_CMD" ".pbase_lets_encrypt.executeCertbotCmd" "true"

parseConfig "EMAIL_ADDR" ".pbase_lets_encrypt.emailAddress" "yoursysadmin@yourrealmail.com"
parseConfig "ADDITIONAL_SUBDOMAIN" ".pbase_lets_encrypt.additionalSubDomain" ""

echo "CONFIG_ENABLE_AUTORENEW: $CONFIG_ENABLE_AUTORENEW"
echo "EXECUTE_CERTBOT_CMD:     $EXECUTE_CERTBOT_CMD"
echo "EMAIL_ADDR:              $EMAIL_ADDR"
echo "ADDITIONAL_SUBDOMAIN:    $ADDITIONAL_SUBDOMAIN"

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
echo "Domain list has WWW:     ${DOMAIN_NAME_LIST_HAS_WWW}"

## Check for /etc/httpd/conf.d/ssl.conf, comment it out if it exists
commentOutFile "/etc/httpd/conf.d" "ssl.conf"


## when DB_PSWD is populated below that means DB config has been defined
DB_PSWD=""

if [[ $DATABASE == "postgres" ]]; then
  PBASE_CONFIG_FILENAME="pbase_postgres.json"
  locateConfigFile "$PBASE_CONFIG_FILENAME"
  parseConfig "DB_HOSTNAME" ".pbase_postgres[0].default.hostName" "localhost"
  parseConfig "DB_PORT"     ".pbase_postgres[0].default.port" "5432"
  parseConfig "DB_NAME"     ".pbase_postgres[0].default.database[0].name" "gitea"
  parseConfig "DB_USER"     ".pbase_postgres[0].default.database[0].user" "gitea"
  parseConfig "DB_CHARSET"  ".pbase_postgres[0].default.database[0].characterSet" "UTF8"
  parseConfig "DB_PSWD"     ".pbase_postgres[0].default.database[0].password" ""

elif [[ $DATABASE == "mysql" ]]; then
  PBASE_CONFIG_FILENAME="pbase_mysql.json"
  locateConfigFile "$PBASE_CONFIG_FILENAME"
  parseConfig "DB_HOSTNAME" ".pbase_mysql[0].default.hostName" "localhost"
  parseConfig "DB_PORT"     ".pbase_mysql[0].default.port" "3306"
  parseConfig "DB_NAME"     ".pbase_mysql[0].default.database[0].name" "gitea"
  parseConfig "DB_USER"     ".pbase_mysql[0].default.database[0].user" "gitea"
  parseConfig "DB_CHARSET"  ".pbase_mysql[0].default.characterSet" "utf8mb48"
  parseConfig "DB_PSWD"     ".pbase_mysql[0].default.database[0].password" ""
fi

PATH_TO_DBCONFIG="/usr/local/pbase-data/admin-only/module-config.d/${PBASE_CONFIG_FILENAME}"

echo ""
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

echo ""
echo "Nextcloud base:          ${VAR_WWW_ROOT}/nextcloud"
#echo "Apache alias config:     /etc/httpd/conf.d/nextcloud.conf"
#/bin/cp --no-clobber /usr/local/pbase-data/pbase-nextcloud/etc-httpd-confd/nextcloud.conf /etc/httpd/conf.d/

echo "Apache vhost template:   /etc/httpd/conf.d/nextcloud-vhost.conf"
echo "FULLDOMAINNAME:          $FULLDOMAINNAME"
/bin/cp --no-clobber /usr/local/pbase-data/pbase-nextcloud/etc-httpd-confd/nextcloud-vhost.conf /etc/httpd/conf.d/

if [[ -e "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf" ]] ; then
  echo "Removing existing:       /etc/httpd/conf.d/${FULLDOMAINNAME}.conf"
  mv "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"  "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf-DISABLED"

  ## set aside conf file so that certbot can recreate the ...le-ssl.conf
  if [[ -e "/etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf" ]] ; then
    echo "Disabling prev conf:     /etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf"
    mv "/etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf" "/etc/httpd/conf.d/${FULLDOMAINNAME}-le-ssl.conf-DISABLED"
  fi
fi

## replace your.server.com in template conf
sed -i "s/your.server.com/${FULLDOMAINNAME}/" "/etc/httpd/conf.d/nextcloud-vhost.conf"

## may also enable www alias
sed -i "s/www.server.com/www.${THISDOMAINNAME}/" "/etc/httpd/conf.d/nextcloud-vhost.conf"

if [[ "${DOMAIN_NAME_LIST_HAS_WWW}" != "" ]] ; then
  echo "Enabling:                ServerAlias www.${THISDOMAINNAME}"
  sed -i "s/# ServerAlias www/ServerAlias www/" "/etc/httpd/conf.d/nextcloud-vhost.conf"
fi


## rename template conf file to match the full domain name
echo "Nextcloud proxy:         /etc/httpd/conf.d/${FULLDOMAINNAME}.conf"
mv "/etc/httpd/conf.d/nextcloud-vhost.conf" "/etc/httpd/conf.d/${FULLDOMAINNAME}.conf"

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

echo ""
IMAGEMAGIK_PHP_INI="/etc/php.d/20-imagick.ini"

## add imagemagik php extension
if [[ -e "${IMAGEMAGIK_PHP_INI}" ]]; then
  echo "Already exists:          ${IMAGEMAGIK_PHP_INI}"
else
  echo "Invoking:                pecl install imagick"
  pecl channel-update pecl.php.net
  pecl -q install imagick

  echo ""
  echo "Adding PHP extension:    ${IMAGEMAGIK_PHP_INI}"
  echo "extension=imagick.so" > ${IMAGEMAGIK_PHP_INI}
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

echo "Default PBase module configuration directory:"
echo "                         /usr/local/pbase-data/admin-only/module-config.d/"

INSTALLED_DOMAIN_URI="${THISDOMAINNAME}${SLASH_NEXTCLOUD_URLSUBPATH}"

if [[ "$URL_SUBDOMAIN" != "" ]] ; then
  INSTALLED_DOMAIN_URI="${FULLDOMAINNAME}"
fi

echo "Configured database:     $PATH_TO_DBCONFIG"
cat $PATH_TO_DBCONFIG

echo ""
echo "NextCloud web application is running."
echo "Next step - Open this URL to complete the install:"
echo "if locally installed"
echo "                         http://localhost${SLASH_NEXTCLOUD_URLSUBPATH}"
echo "if hostname is accessible"
echo "                         http://${INSTALLED_DOMAIN_URI}"
echo "or if your domain is registered in DNS and has HTTPS enabled"
echo "                         https://${INSTALLED_DOMAIN_URI}"
echo ""

%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-nextcloud/etc-httpd-confd/nextcloud.conf
/usr/local/pbase-data/pbase-nextcloud/etc-httpd-confd/nextcloud-vhost.conf
