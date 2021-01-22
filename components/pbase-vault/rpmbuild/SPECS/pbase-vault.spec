Name: pbase-vault
Version: 1.0
Release: 0
Summary: PBase Hashicorp Vault service rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-vault-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-vault
Requires: unzip,wget,jq

%description
PBase Vault service

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


echo "PBase Vault service"

## config is stored in json file with root-only permissions
##     /usr/local/pbase-data/admin-only/module-config.d/pbase_apache.json


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

check_linux_version

## look for config file "pbase_vault.json"
PBASE_CONFIG_FILENAME="pbase_vault.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "DEV_MODE" ".pbase_vault.devMode" "false"
parseConfig "HTTP_PORT" ".pbase_vault.httpPort" "8200"
parseConfig "ENABLE_EXTERNAL_ACCESS" ".pbase_vault.firewallEnableExternalAccess" "true"

parseConfig "ADD_APACHE_PROXY" ".pbase_vault.addApacheProxy" "false"
parseConfig "STORAGE_FILE_PATH" ".pbase_vault.storageFilePath" "true"

echo "HTTP_PORT:               $HTTP_PORT"
echo "DEV_MODE:                $DEV_MODE"
##echo "ADD_APACHE_PROXY:        $ADD_APACHE_PROXY"

## check if already installed
if [[ -e "/usr/local/bin/vault" ]]; then
  echo "Vault executable /usr/local/bin/vault already exists - exiting"
  exit 0
fi


echo "Creating user:           vault"
useradd --system --home /etc/vault --shell /bin/false vault

## echo "Creating directories:    /opt/vault/{logs,bin,data}"
echo "                         /etc/vault"

## mkdir -p /opt/vault/{logs,bin,data}
mkdir /etc/vault

chown -R vault:vault /etc/vault
## chown -R vault:vault /opt/vault/


echo "Downloading Vault server binary"

cd /usr/local/pbase-data/pbase-vault

VAULT_VERS="1.6.0"
wget -q -O vault.zip https://releases.hashicorp.com/vault/${VAULT_VERS}/vault_${VAULT_VERS}_linux_amd64.zip
unzip vault.zip -d /usr/local/bin

echo "Downloaded file from hashicorp.com:"
ls -lh /usr/local/bin/vault

#echo "Config file:             /etc/vault/config.json"
/bin/cp --no-clobber /usr/local/pbase-data/pbase-vault/etc-vault/config.json /etc/vault/

echo "System config:           setcap cap_ipc_lock=+ep /usr/local/bin/vault"
setcap cap_ipc_lock=+ep /usr/local/bin/vault

echo "Service:                 /etc/systemd/system/vault.service"

if [[ $DEV_MODE == "true" ]] ; then
  echo "Setting Vault dev-mode"
  /bin/cp --no-clobber /usr/local/pbase-data/pbase-vault/etc-systemd-system-devmode/vault.service /etc/systemd/system/
else
  /bin/cp --no-clobber /usr/local/pbase-data/pbase-vault/etc-systemd-system/vault.service /etc/systemd/system/
fi

/bin/cp --no-clobber /usr/local/pbase-data/pbase-vault/etc-vault/config.json /etc/vault/

echo "To use vault cmd line immediately set VAULT_ADDR with:"
echo "export VAULT_ADDR='http://127.0.0.1:8200'"
#echo "...then launch vault in dev mode with:"
#echo "vault server -dev"
#echo ""

systemctl daemon-reload
systemctl enable vault
systemctl start vault

systemctl status vault

if [[ $DEV_MODE == "true" ]] ; then
  echo "Next steps: find your Unseal Key and Root token with this journalctl command."
  echo ""
  echo "journalctl -u vault --no-pager | grep 'Root Token\|Unseal Key'"
  echo ""
else
  echo "Next steps: Follow the docmentation to unseal the Vault using vault command-line or Web UI."
  echo ""
fi


echo "Vault service running and ready to be configured"
echo "Vault Web UI at:         http://127.0.0.1:8200/ui"
echo ""
##TODO escape quotes: ## append_bashrc_alias showvaultkey "journalctl -u vault --no-pager | grep 'Root Token\|Unseal Key'"


if [[ "${ENABLE_EXTERNAL_ACCESS}" == "true" ]] ; then
  echo "Opening firewall port:   8200"

  /bin/firewall-cmd --zone=public --add-port=8200/tcp --permanent
  /bin/firewall-cmd --reload

  /bin/systemctl restart firewalld || fail "failed to restart firewalld service"
fi


echo "Installing VAULT_ADDR env-variable in: /etc/profile.d"
/bin/cp -rf /usr/local/pbase-data/pbase-vault/etc-profile-d/*.sh /etc/profile.d

THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

if [[ "$ADD_APACHE_PROXY" == "true" ]] ; then

  echo "Adding /vault proxy"
  /bin/cp --no-clobber /usr/local/pbase-data/pbase-vault/etc-httpd-confd/vault-proxy.conf /etc/httpd/conf.d/vault-proxy.conf

  echo "                         http://${THISDOMAINNAME}/vault"
  echo "or"
  echo "                         http://${THISHOSTNAME}/vault"
fi

## add shell aliases
append_bashrc_alias tailvault "tail -f -n20 /opt/vault/logs/vault.log"
append_bashrc_alias editvaultconf "vi /etc/vault/config.json"


%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-vault/etc-profile-d/pbase-vault-addr.sh
/usr/local/pbase-data/pbase-vault/etc-systemd-system/vault.service
/usr/local/pbase-data/pbase-vault/etc-systemd-system-devmode/vault.service
/usr/local/pbase-data/pbase-vault/etc-vault/config.json
/usr/local/pbase-data/pbase-vault/etc-httpd-confd/vault-proxy.conf
