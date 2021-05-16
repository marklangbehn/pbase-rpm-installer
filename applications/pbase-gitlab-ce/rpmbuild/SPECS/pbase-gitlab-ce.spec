Name: pbase-gitlab-ce
Version: 1.0
Release: 1
Summary: PBase GitLab CE service rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-gitlab-ce
Requires: pbase-epel, jq, git, gitlab-ce

%description
PBase GitLab CE service

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


echo "PBase GitLab CE service"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

## config is stored in json file with root-only permissions
## it can be one of two places:
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


## look for config file "pbase_gitlab_ce.json"
PBASE_CONFIG_FILENAME="pbase_gitlab_ce.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "EXTERN_URL_SUBDOMAIN" ".pbase_gitlab_ce.urlSubDomain" "git"
parseConfig "EXTERN_URL_IS_HTTPS" ".pbase_gitlab_ce.externalUrlIsHttps" "true"
parseConfig "LETS_ENCRYPT_ENABLE" ".pbase_gitlab_ce.letsEncryptEnable" "true"

parseConfig "LETS_ENCRYPT_EMAILADDR" ".pbase_gitlab_ce.letsEncryptEmailAddress" "nobody@nowhere.net"
parseConfig "CRONTAB_BACKUP_ENABLE" ".pbase_gitlab_ce.crontabBackupEnable" "true"
parseConfig "CRONTAB_BACKUP_HOUR" ".pbase_gitlab_ce.crontabBackupHour" "2"

echo "EXTERN_URL_SUBDOMAIN:    $EXTERN_URL_SUBDOMAIN"
echo "EXTERN_URL_IS_HTTPS:     $EXTERN_URL_IS_HTTPS"
echo "LETS_ENCRYPT_ENABLE:     $LETS_ENCRYPT_ENABLE"
echo "LETS_ENCRYPT_EMAILADDR:  $LETS_ENCRYPT_EMAILADDR"

THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

## FULLDOMAINNAME is the subdomain if declared plus the domain
FULLDOMAINNAME="${THISDOMAINNAME}"

if [[ "${EXTERN_URL_SUBDOMAIN}" != "" ]] ; then
  FULLDOMAINNAME="${EXTERN_URL_SUBDOMAIN}.${THISDOMAINNAME}"
  echo "Using subdomain:         ${FULLDOMAINNAME}"
fi

if [[ $EXTERN_URL_IS_HTTPS == "true" ]]; then
  EXTERNALURL="https://${FULLDOMAINNAME}"
else
  EXTERNALURL="http://${FULLDOMAINNAME}"
fi

QT="'"
EXTERNALURLQUOTED=${QT}${EXTERNALURL}${QT}
LE_EMAILADDRQUOTED=${QT}${LETS_ENCRYPT_EMAILADDR}${QT}


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
  echo "LE_EMAILADDRQUOTED:      $LE_EMAILADDRQUOTED"
  sed -i "s/^# letsencrypt\['contact_emails'] = \[]/letsencrypt['contact_emails'] = [ $LE_EMAILADDRQUOTED ] /" /etc/gitlab/gitlab.rb
fi


#if [[ $CRONTAB_BACKUP_ENABLE == "true" ]]; then
#  echo "CRONTAB_BACKUP_ENABLE:   $CRONTAB_BACKUP_ENABLE"
#  echo "CRONTAB_BACKUP_HOUR:     $CRONTAB_BACKUP_HOUR"
#  ##sed -i "s/^external_url \'http:\/\/gitlab\.example\.com\'/external_url $EXTERNALURLQUOTED/" /etc/gitlab/gitlab.rb
#fi

## finish setup after setting config
echo "Executing:               gitlab-ctl reconfigure"
gitlab-ctl reconfigure

echo ""
## add shell aliases
append_bashrc_alias tailgitlab "gitlab-ctl tail"
append_bashrc_alias startgitlab "gitlab-ctl start"
append_bashrc_alias restartgitlab "gitlab-ctl restart"
append_bashrc_alias stopgitlab "gitlab-ctl stop"
append_bashrc_alias statusgitlab "gitlab-ctl status"

append_bashrc_alias statusallgitlab "systemctl status gitlab-runsvdir"
append_bashrc_alias editgitlabconf "vi /etc/gitlab/gitlab.rb"

echo "GitLab service ready"
echo "Next step - required - Open this URL to create the password for "
echo "                       the GitLab 'root' account."
echo "                         ${EXTERNALURL}"
echo ""

%files
