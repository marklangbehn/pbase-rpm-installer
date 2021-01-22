Name: pbase-node-solid-server
Version: 1.0
Release: 0
Summary: PBase Node Solid Server rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-node-solid-server-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-node-solid-server
Requires: nodejs, pbase-apache, pbase-lets-encrypt-transitive-dep


%description
PBase Node Solid Server

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


echo "PBase Node Solid Server installer"

## config is stored in json file with root-only permissions
## it can be one of two places:
##     /usr/local/pbase-data/admin-only/pbase_module_config.json
## or
##     /usr/local/pbase-data/admin-only/module-config.d/pbase_node_solid_server.json


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_node_solid_server.json"
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
echo "Default PBase module configuration directory:"
echo "                        /usr/local/pbase-data/admin-only/module-config.d/"

## look for config file "pbase_gitea.json"
PBASE_CONFIG_FILENAME="pbase_node_solid_server.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
#parseConfig "CONFIG_DATABASE" ".pbase_node_solid_server.database" ""
parseConfig "ADD_APACHE_PROXY" ".pbase_node_solid_server.addApacheProxy" "true"
parseConfig "CONFIG_SUBDOMAIN_NAME" ".pbase_node_solid_server.urlSubDomain" "solid"
parseConfig "CONFIG_URLSUBPATH" ".pbase_node_solid_server.urlSubPath" ""

#echo "CONFIG_DATABASE:         $CONFIG_DATABASE"
echo "ADD_APACHE_PROXY:        $ADD_APACHE_PROXY"
echo "CONFIG_USE_SUBDOMAIN:    $CONFIG_USE_SUBDOMAIN"
echo "CONFIG_SUBDOMAIN_NAME:   $CONFIG_SUBDOMAIN_NAME"
echo "CONFIG_URLSUBPATH:       $CONFIG_URLSUBPATH"

SLASH_SOLID_URLSUBPATH=""

if [[ "${CONFIG_URLSUBPATH}" != "" ]]; then
  SLASH_SOLID_URLSUBPATH="/${CONFIG_URLSUBPATH}"
fi

echo "SLASH_SOLID_URLSUBPATH: ${SLASH_SOLID_URLSUBPATH}"


## Let's Encrypt config
PBASE_CONFIG_FILENAME="pbase_lets_encrypt.json"
locateConfigFile "$PBASE_CONFIG_FILENAME"
URL_SUBDOMAIN=""

parseConfig "URL_SUBDOMAIN" ".pbase_lets_encrypt.urlSubDomain" ""

## fetch config value from JSON file
parseConfig "CONFIG_ENABLE_AUTORENEW" ".pbase_lets_encrypt.enableAutoRenew" "true"
parseConfig "EXECUTE_CERTBOT_CMD" ".pbase_lets_encrypt.executeCertbotCmd" "true"
parseConfig "EMAIL_ADDR" ".pbase_lets_encrypt.emailAddress" "yoursysadmin@yourrealmail.com"
parseConfig "ADDITIONAL_SUBDOMAIN" ".pbase_lets_encrypt.additionalSubDomain" ""

echo "CONFIG_ENABLE_AUTORENEW: $CONFIG_ENABLE_AUTORENEW"
echo "EXECUTE_CERTBOT_CMD:     $EXECUTE_CERTBOT_CMD"
echo "EMAIL_ADDR:              $EMAIL_ADDR"
echo "URL_SUBDOMAIN:           ${URL_SUBDOMAIN}"
#echo "ADDITIONAL_SUBDOMAIN:    $ADDITIONAL_SUBDOMAIN"


##echo "Creating user:           solid"
##adduser --system --gid apache --no-create-home solid

THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

## FULLDOMAINNAME is the subdomain if declared plus the domain
FULLDOMAINNAME="${THISDOMAINNAME}"

if [[ "$CONFIG_SUBDOMAIN_NAME" != "" ]] ; then
  FULLDOMAINNAME="${CONFIG_SUBDOMAIN_NAME}.${THISDOMAINNAME}"
  echo "Using subdomain:         ${FULLDOMAINNAME}"
fi

DASH_D_ADDITIONAL_SUBDOMAIN=""
if [[ $ADDITIONAL_SUBDOMAIN != "" ]] ; then
  DASH_D_ADDITIONAL_SUBDOMAIN="-d $ADDITIONAL_SUBDOMAIN.$THISDOMAINNAME"
fi



echo "Installing Node Solid server from solidproject.org"

VAR_WWW_ROOT="/var/www/${FULLDOMAINNAME}"


mkdir -p $VAR_WWW_ROOT
cd $VAR_WWW_ROOT
mkdir -p config/ data/ .db/
touch config.json

##chown -R solid:apache $VAR_WWW_ROOT

## disable unused config file: apache ssl.conf
if [[ -e "/etc/httpd/conf.d/ssl.conf" ]] ; then
  mv "/etc/httpd/conf.d/ssl.conf" "/etc/httpd/conf.d/ssl.conf-DISABLED"
fi


echo "Executing:               npm install -g solid-server"
cd $VAR_WWW_ROOT
npm install -g solid-server


echo "Solid base:              ${VAR_WWW_ROOT}"

echo "Apache vhost config:     /etc/httpd/conf.d/node-solid-server-proxy.conf"
echo "FULLDOMAINNAME:          $FULLDOMAINNAME"
/bin/cp --no-clobber /usr/local/pbase-data/pbase-node-solid-server/etc-httpd-confd/node-solid-server-proxy.conf /etc/httpd/conf.d/

## replace domain name yourhost.example.org in template conf
sed -i "s/yourhost.example.org/${FULLDOMAINNAME}/" "/etc/httpd/conf.d/node-solid-server-proxy.conf"

echo "Removing previous vhost:"
cd /etc/httpd/conf.d/
ls -l $(hostname -d)*.conf

## move old conf file to /root rather than delete them
mv $(hostname -d)*.conf ~

echo "Enabling solid service"
echo "Systemd file:            /etc/systemd/system/solid.service"
/bin/cp --no-clobber /usr/local/pbase-data/pbase-node-solid-server/etc-systemd-system/solid.service  /etc/systemd/system/
sed -i "s/yourhost.example.org/${FULLDOMAINNAME}/" "/etc/systemd/system/solid.service"

echo "Configure solid service: ${VAR_WWW_ROOT}/config.json"
/bin/cp -f /usr/local/pbase-data/pbase-node-solid-server/config/config.json  "${VAR_WWW_ROOT}/"

sed -i "s/yourhost.example.org/${FULLDOMAINNAME}/" "${VAR_WWW_ROOT}/config.json"
sed -i "s/example.org/${THISDOMAINNAME}/" "${VAR_WWW_ROOT}/config.json"


/bin/systemctl daemon-reload
/bin/systemctl enable solid

echo "Starting solid:          systemctl start solid"
systemctl start solid

echo "Restarting Apache:       systemctl restart httpd"
systemctl restart httpd


## add shell aliases
append_bashrc_alias editsolidserverconf "vi ${VAR_WWW_ROOT}/config.json"


INSTALLED_DOMAIN_URI="${THISDOMAINNAME}${SLASH_SOLID_URLSUBPATH}"

if [[ "$CONFIG_USE_SUBDOMAIN" == "true" ]] && [[ "$CONFIG_SUBDOMAIN_NAME" != "" ]] ; then
  INSTALLED_DOMAIN_URI="${FULLDOMAINNAME}"
fi

echo ""
echo "Solid server is running."
echo "Next step - Open this URL to complete the install:"
echo "if locally installed"
echo "                         http://localhost${SLASH_SOLID_URLSUBPATH}"
echo "if hostname is accessible"
echo "                         http://${INSTALLED_DOMAIN_URI}"
echo "or if your domain is registered in DNS and has HTTPS enabled"
echo "                         https://${INSTALLED_DOMAIN_URI}"
echo ""


%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-node-solid-server/etc-httpd-confd/node-solid-server-proxy.conf
/usr/local/pbase-data/pbase-node-solid-server/config/config.json
/usr/local/pbase-data/pbase-node-solid-server/config/config.json-default
/usr/local/pbase-data/pbase-node-solid-server/etc-systemd-system/solid.service
