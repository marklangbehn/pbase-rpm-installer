Name: pbase-gitlab-ce
Version: 1.0
Release: 0
Summary: PBase GitLab CE service rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-gitlab-ce-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-gitlab-ce
Requires: pbase-epel, jq, git, gitlab-ce

%description
PBase GitLab CE service

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


echo "PBase GitLab CE service"

## config is stored in json file with root-only permissions
## it can be one of two places:
##     /usr/local/pbase-data/admin-only/pbase_module_config.json
## or
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


## look for either separate config file "pbase_gitlab.json" or all-in-one file: "pbase_module_config.json"
PBASE_CONFIG_FILENAME="pbase_gitlab.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "EXTERN_URL_SUBDOMAIN" ".pbase_gitlab.externalUrlSubdomain" "gitlab"
parseConfig "EXTERN_URL_IS_HTTPS" ".pbase_gitlab.externalUrlIsHttps" "true"
parseConfig "LETS_ENCRYPT_ENABLE" ".pbase_gitlab.letsEncryptEnable" "true"

parseConfig "LETS_ENCRYPT_EMAILADDR" ".pbase_gitlab.letsEncryptEmailAddress" "nobody@nowhere.net"
parseConfig "CRONTAB_BACKUP_ENABLE" ".pbase_gitlab.crontabBackupEnable" "true"
parseConfig "CRONTAB_BACKUP_HOUR" ".pbase_gitlab.crontabBackupHour" "2"

echo "EXTERN_URL_SUBDOMAIN:    $EXTERN_URL_SUBDOMAIN"
echo "EXTERN_URL_IS_HTTPS:     $EXTERN_URL_IS_HTTPS"
echo "LETS_ENCRYPT_ENABLE:     $LETS_ENCRYPT_ENABLE"
echo "LETS_ENCRYPT_EMAILADDR:  $LETS_ENCRYPT_EMAILADDR"

THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

if [[ $EXTERN_URL_IS_HTTPS == "true" ]]; then
  EXTERNALURL="https://$EXTERN_URL_SUBDOMAIN.$THISDOMAINNAME"
else
  EXTERNALURL="http://$EXTERN_URL_SUBDOMAIN.$THISDOMAINNAME"
fi

QT="'"
EXTERNALURLQUOTED=${QT}${EXTERNALURL}${QT}
LE_EMAILADDRQUOTED=${QT}${LETS_ENCRYPT_EMAILADDR}${QT}


## check if already installed
#if [[ -d "/var/lib/gitea" ]]; then
#  echo "/var/lib/gitea directory already exists - exiting"
#  exit 0
#fi

if [[ ! -e /etc/gitlab/gitlab.rb ]] ; then
  echo "Cannot configure:        /etc/gitlab/gitlab.rb"
  exit 1;
fi

echo "Configuring GitLab CE server"
echo "Setting external_url:    /etc/gitlab/gitlab.rb"
#echo "EXTERNALURLQUOTED:       $EXTERNALURLQUOTED"

/bin/cp -p /etc/gitlab/gitlab.rb /etc/gitlab/gitlab-ORIG.rb

## replace example hostname, use '#' as delimiter
sed  -i  "s#http\://gitlab\.example\.com#${EXTERNALURL}#g" /etc/gitlab/gitlab.rb


if [[ $LETS_ENCRYPT_ENABLE == "true" ]]; then
  echo "LETS_ENCRYPT_ENABLE = true"
  sed -i "s/^# letsencrypt\['enable'] = nil/letsencrypt['enable'] = true/" /etc/gitlab/gitlab.rb
fi


if [[ $LETS_ENCRYPT_EMAILADDR != "" ]]; then
  echo "LE_EMAILADDRQUOTED:  $LE_EMAILADDRQUOTED"
  sed -i "s/^# letsencrypt\['contact_emails'] = \[]/letsencrypt['contact_emails'] = [ $LE_EMAILADDRQUOTED ] /" /etc/gitlab/gitlab.rb
fi


if [[ $CRONTAB_BACKUP_ENABLE == "true" ]]; then
  echo "CRONTAB_BACKUP_ENABLE:       $CRONTAB_BACKUP_ENABLE"
  echo "CRONTAB_BACKUP_HOUR:         $CRONTAB_BACKUP_HOUR"

  ##sed -i "s/^external_url \'http:\/\/gitlab\.example\.com\'/external_url $EXTERNALURLQUOTED/" /etc/gitlab/gitlab.rb
fi

## finish setup after setting config
echo "Executing:               gitlab-ctl reconfigure"
gitlab-ctl reconfigure

## add shell aliases
append_bashrc_alias restartgitlab "gitlab-ctl restart"
append_bashrc_alias tailgitlab "gitlab-ctl tail"
append_bashrc_alias editgitlabconf "vi /etc/gitlab/gitlab.rb"

echo "GitLab service running. Open this URL to complete install."
echo "Next steps - login first time to setup your password and account"
echo "                         http://$EXTERN_URL_SUBDOMAIN.$THISDOMAINNAME"
echo ""

%files
%defattr(-,root,root,-)
/usr/local/pbase-data/pbase-gitlab-ce/etc-httpd-confd/gitlab-proxy.conf