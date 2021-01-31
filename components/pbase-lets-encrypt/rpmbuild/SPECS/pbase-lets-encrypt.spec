Name: pbase-lets-encrypt
Version: 1.0
Release: 0
Summary: PBase Let's Encrypt configure
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-lets-encrypt
Requires: pbase-lets-encrypt-transitive-dep, pbase-epel, jq

%description
Configure Let's Encrypt

%prep

%install

%clean

%pre

%post
echo "rpm postinstall $1"

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


echo "PBase Let's Encrypt certbot setup and issue HTTPS certificate"

## config is stored in json file with root-only permissions
##     /usr/local/pbase-data/admin-only/module-config.d/pbase_lets_encrypt.json


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_lets_encrypt.json"
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

THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

check_linux_version

## look for config file "pbase_lets_encrypt.json"
PBASE_CONFIG_FILENAME="pbase_lets_encrypt.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "CONFIG_ENABLE_AUTORENEW" ".pbase_lets_encrypt.enableAutoRenew" "true"
parseConfig "EXECUTE_CERTBOT_CMD" ".pbase_lets_encrypt.executeCertbotCmd" "true"

parseConfig "EMAIL_ADDR" ".pbase_lets_encrypt.emailAddress" "yoursysadmin@yourrealmail.com"
parseConfig "URL_SUBDOMAIN" ".pbase_lets_encrypt.urlSubDomain" ""
parseConfig "ADDITIONAL_SUBDOMAIN" ".pbase_lets_encrypt.additionalSubDomain" ""

echo "CONFIG_ENABLE_AUTORENEW: $CONFIG_ENABLE_AUTORENEW"
echo "EXECUTE_CERTBOT_CMD:     $EXECUTE_CERTBOT_CMD"
echo "EMAIL_ADDR:              $EMAIL_ADDR"
echo "URL_SUBDOMAIN:           $URL_SUBDOMAIN"
echo "ADDITIONAL_SUBDOMAIN:    $ADDITIONAL_SUBDOMAIN"


echo ""
echo "hostname:                $THISHOSTNAME"
echo "domainname:              $THISDOMAINNAME"

## when doing additonal domain like www.example.com
DASH_D_ADDITIONAL_SUBDOMAIN=""
if [[ $ADDITIONAL_SUBDOMAIN != "" ]] ; then
  DASH_D_ADDITIONAL_SUBDOMAIN="-d $ADDITIONAL_SUBDOMAIN.$THISDOMAINNAME"
  echo "additional subdomain:    $DASH_D_ADDITIONAL_SUBDOMAIN"
fi

## when doing subdomain only like mattermost.example.com
FULLDOMAINNAME="$THISDOMAINNAME"
if [[ $URL_SUBDOMAIN != "" ]] ; then
  FULLDOMAINNAME="$URL_SUBDOMAIN.$THISDOMAINNAME"
  echo "exclusive subdomain:     $FULLDOMAINNAME"
fi


## Add CRON job to run monitorItemImport.pl
PREEXISTING_CRONJOB=`grep certbot /etc/crontab`

CRONJOB_SCRIPT="/usr/bin/certbot"
CRONJOB_LOGFILE="/var/log/letsencrypt-sslrenew.log"

RAND_MINUTE="$((2 + RANDOM % 57))"
echo "RAND_MINUTE:             $RAND_MINUTE"

## line to add to crontab
if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]] || [[ "${REDHAT_RELEASE_DIGIT}" == "8" ]]; then
  CRONJOB_LINE="47 2 * * * root certbot renew >> $CRONJOB_LOGFILE"
  ##CRONJOB_LINE="$RAND_MINUTE 2 * * * root certbot renew >> $CRONJOB_LOGFILE"
else
  ##CRONJOB_LINE="$RAND_MINUTE 2 * * * root /usr/bin/certbot renew >> $CRONJOB_LOGFILE"
  CRONJOB_LINE="47 2 * * * root /usr/bin/certbot renew >> $CRONJOB_LOGFILE"
fi

if [[ ${CONFIG_ENABLE_AUTORENEW} == "false" ]] ; then
  ## comment out the line if autorenew flag is false
  CRONJOB_LINE="## ${CRONJOB_LINE}"
fi

if [[ -e "$CRONJOB_SCRIPT" ]]; then
  if [[ "$PREEXISTING_CRONJOB" == "" ]]; then
    echo "Adding certbot renew:    /etc/crontab"
    echo "                         $CRONJOB_LINE"
    echo "Next Step:"
##  echo "cronjob MUST be manually enabled: vim /etc/crontab"
    echo "  check for renewal certbot logfile: $CRONJOB_LOGFILE"
    echo ""

    echo ""                                                 >>  /etc/crontab
    echo "## Added by pbase-lets-encrypt RPM ##"            >>  /etc/crontab
    echo ""                                                 >>  /etc/crontab
    echo "$CRONJOB_LINE"                                    >>  /etc/crontab

    touch "$CRONJOB_LOGFILE"
  else
    echo "Existing Let's Encrypt:  /etc/crontab"
  fi
else
    echo "No cronjob script found: $CRONJOB_SCRIPT"
fi


if [[ -e "/etc/httpd/conf.d/ssl.conf" ]] ; then
  mv "/etc/httpd/conf.d/ssl.conf" "/etc/httpd/conf.d/ssl.conf-DISABLED"
fi

# Enable httpd service at boot-time, and start httpd service
echo "Restarting service:      httpd"

if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  /sbin/chkconfig httpd --level 345 on || fail "chkconfig failed to enable httpd service"
  /sbin/service httpd restart || fail "failed to restart httpd service"

  ## get SSL cert, will add file in /etc/httpd/conf...
  ## for example:   certbot --apache --agree-tos --email yoursysadmin@yourrealmail.com  -d pbase-foundation.com -d www.pbase-foundation.com -n

  echo "Invoke certbot:          certbot --apache --agree-tos --email ${EMAIL_ADDR} -d ${FULLDOMAINNAME} $DASH_D_ADDITIONAL_SUBDOMAIN -n"
  echo ""
  certbot --apache --agree-tos --email ${EMAIL_ADDR} -d ${FULLDOMAINNAME} $DASH_D_ADDITIONAL_SUBDOMAIN -n

  echo "Restarting service:      httpd"
  /sbin/chkconfig httpd --level 345 on || fail "chkconfig failed to enable httpd service"
  /sbin/service httpd restart || fail "failed to restart httpd service"

elif [[ "${REDHAT_RELEASE_DIGIT}" == "7" ]]; then
  /bin/systemctl daemon-reload
  /bin/systemctl enable httpd.service || fail "systemctl failed to enable httpd service"
  /bin/systemctl restart httpd || fail "failed to restart httpd service"

  ## get SSL cert, may add file in /etc/httpd/conf...
  echo "Invoke certbot:          certbot --apache -d ${FULLDOMAINNAME} $DASH_D_ADDITIONAL_SUBDOMAIN -m ${EMAIL_ADDR} --agree-tos -n"
  echo ""

  if [[ $EXECUTE_CERTBOT_CMD == "true" ]] ; then
     certbot --apache -d ${FULLDOMAINNAME} $DASH_D_ADDITIONAL_SUBDOMAIN -m ${EMAIL_ADDR} --agree-tos -n

     echo "Restarting service:      httpd"
     /bin/systemctl daemon-reload
     /bin/systemctl enable httpd.service || fail "systemctl failed to enable httpd service"
     /bin/systemctl restart httpd || fail "failed to restart httpd service"
     /bin/systemctl status httpd
  else
     echo "EXECUTE_CERTBOT_CMD override: $EXECUTE_CERTBOT_CMD"
  fi

elif [[ "${REDHAT_RELEASE_DIGIT}" == "8" ]]; then

  echo "Invoke certbot:          certbot --no-bootstrap --apache --agree-tos --email ${EMAIL_ADDR}  -d ${FULLDOMAINNAME} $DASH_D_ADDITIONAL_SUBDOMAIN -n"
  echo ""

  if [[ $EXECUTE_CERTBOT_CMD == "true" ]] ; then
    certbot --no-bootstrap --apache --agree-tos --email ${EMAIL_ADDR}  -d ${FULLDOMAINNAME} $DASH_D_ADDITIONAL_SUBDOMAIN -n

    echo "Restarting service:      httpd"
    /bin/systemctl daemon-reload
    /bin/systemctl enable httpd.service || fail "systemctl failed to enable httpd service"
    /bin/systemctl restart httpd || fail "failed to stop httpd service"
  else
    echo "EXECUTE_CERTBOT_CMD override: $EXECUTE_CERTBOT_CMD"
  fi
else
  echo "Not supported REDHAT_RELEASE_DIGIT: ${REDHAT_RELEASE_DIGIT}"
fi


echo "/etc/httpd/conf.d/"
ls -l /etc/httpd/conf.d/

append_bashrc_alias taillecronjoblog "tail -f $CRONJOB_LOGFILE"
append_bashrc_alias editcrontab "vi /etc/crontab"
exit 0

%files
