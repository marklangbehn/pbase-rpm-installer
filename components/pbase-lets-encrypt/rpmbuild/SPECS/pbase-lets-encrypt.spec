Name: pbase-lets-encrypt
Version: 1.0
Release: 6
Summary: PBase Let's Encrypt configure
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-lets-encrypt
Requires: pbase-lets-encrypt-transitive-dep, pbase-epel, jq, pbase-firewall-enable

%description
Configure Let's Encrypt

%prep

%install

%clean

%pre

%post
#echo "rpm postinstall $1"

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

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

## config may be stored in json file with root-only permissions
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
  AMAZON2022_RELEASE=""
  if [[ -e "/etc/system-release" ]]; then
    SYSTEM_RELEASE="$(cat /etc/system-release)"
    AMAZON1_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux AMI')"
    AMAZON2_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux release 2 ')"
    AMAZON2022_RELEASE="$(cat /etc/system-release | grep 'Amazon Linux release 2022')"
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
  elif [[ "$AMAZON2022_RELEASE" != "" ]]; then
    echo "AMAZON2022_RELEASE:      $AMAZON2022_RELEASE"
    REDHAT_RELEASE_DIGIT="9"
    echo "REDHAT_RELEASE_DIGIT:    ${REDHAT_RELEASE_DIGIT}"
  fi
}

commentOutFile() {
  ## disable config file in directory $1 named $2
  echo "Checking for:            ${1}/${2}"

  if [[ -e "${1}/${2}" ]] ; then
    ##echo "Backup:                  ${1}/${2}-ORIG"
    cp -p "${1}/${2}" "${1}/${2}-ORIG"

    ## comment out with a '#' in front of all lines
    echo "Commenting out contents: ${2}"
    sed -i 's/^\([^#].*\)/# \1/g' "${1}/${2}"
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

## check for default email text file
DEFAULT_EMAIL="yoursysadmin@yourrealmail.com"
if [[ -e /root/DEFAULT_EMAIL_ADDRESS.txt ]] ; then
  read -r DEFAULT_EMAIL < /root/DEFAULT_EMAIL_ADDRESS.txt
fi

## check for default subdomain text file
DEFAULT_SUB_DOMAIN=""
if [[ -e /root/DEFAULT_SUB_DOMAIN.txt ]] ; then
  read -r DEFAULT_SUB_DOMAIN < /root/DEFAULT_SUB_DOMAIN.txt
fi

parseConfig "EMAIL_ADDR" ".pbase_lets_encrypt.emailAddress" "${DEFAULT_EMAIL}"
parseConfig "URL_SUBDOMAIN" ".pbase_lets_encrypt.urlSubDomain" "${DEFAULT_SUB_DOMAIN}"
parseConfig "ADDITIONAL_SUBDOMAIN" ".pbase_lets_encrypt.additionalSubDomain" ""


PBASE_CONFIG_FILENAME="pbase_apache.json"
locateConfigFile "$PBASE_CONFIG_FILENAME"
parseConfig "ENABLE_CHECK_FOR_WWW" ".pbase_apache.enableCheckForWww" "true"

echo "CONFIG_ENABLE_AUTORENEW: $CONFIG_ENABLE_AUTORENEW"
echo "ENABLE_CHECK_FOR_WWW:    $ENABLE_CHECK_FOR_WWW"
echo "EXECUTE_CERTBOT_CMD:     $EXECUTE_CERTBOT_CMD"
echo "EMAIL_ADDR:              $EMAIL_ADDR"
echo "URL_SUBDOMAIN:           $URL_SUBDOMAIN"
echo "ADDITIONAL_SUBDOMAIN:    $ADDITIONAL_SUBDOMAIN"

echo ""
echo "Hostname:                $THISHOSTNAME"
echo "Domainname:              $THISDOMAINNAME"


## determine which domain(s) to register
FULLDOMAINNAME="${THISDOMAINNAME}"
WWWDOMAINNAME="www.${THISDOMAINNAME}"
HAS_WWW_SUBDOMAIN="false"
DOMAIN_NAME_LIST=""

## save the command line and domain names used
SAVE_CMD_DIR="/usr/local/pbase-data/admin-only"

if [[ -f "${SAVE_CMD_DIR}/domain-name-list.txt" ]]; then
  read -r DOMAIN_NAME_LIST < "${SAVE_CMD_DIR}/domain-name-list.txt"
  echo "found DOMAIN_NAME_LIST:  ${DOMAIN_NAME_LIST}"
fi

echo "Checking if LE already installed"
if [[ -d "/etc/letsencrypt/live/" ]] ; then
  echo "ls -l /etc/letsencrypt/live/"
  ls -l /etc/letsencrypt/live/
fi

## check if a subdomain has already been added to the DOMAIN_NAME_LIST

if [[ "${URL_SUBDOMAIN}" != "" ]] && [[ "${DOMAIN_NAME_LIST}" != *"${URL_SUBDOMAIN}.${THISDOMAINNAME}"* ]] ; then
  ## when doing subdomain only like myapp.example.com (not registering root domain)
  FULLDOMAINNAME="${URL_SUBDOMAIN}.${THISDOMAINNAME}"
  DOMAIN_NAME_LIST="${FULLDOMAINNAME}"
  echo "Exclusive subdomain:     ${FULLDOMAINNAME}"
elif [[ "${DOMAIN_NAME_LIST}" != *"${URL_SUBDOMAIN}.${THISDOMAINNAME}"* ]] ; then
  ## when doing root domain, check if www is also ping-able
  if [[ $ENABLE_CHECK_FOR_WWW == "true" ]] ; then
    ping -c 1 "${WWWDOMAINNAME}" &> /dev/null

    if [[ "$?" == 0 ]] ; then
      echo "host responded:          ${WWWDOMAINNAME}"
      HAS_WWW_SUBDOMAIN="true"
    else
      echo "no response:             ${WWWDOMAINNAME}"
    fi
  fi

  ## start with root domain first on list
  DOMAIN_NAME_LIST="${THISDOMAINNAME}"

  ## may add www subdomain to list
  if [[ "${HAS_WWW_SUBDOMAIN}" == "true" ]] ; then
    if [[ "${DOMAIN_NAME_LIST}" != "" ]] ; then
      ## add comma to end of list
      DOMAIN_NAME_LIST="${DOMAIN_NAME_LIST},"
    fi
    DOMAIN_NAME_LIST="${DOMAIN_NAME_LIST}www.${THISDOMAINNAME}"
  fi

  ## may add additional subdomain to list
  if [[ "${ADDITIONAL_SUBDOMAIN}" != "" ]] ; then
    if [[ "${DOMAIN_NAME_LIST}" != "" ]] ; then
      ## add comma to end of list
      DOMAIN_NAME_LIST="${DOMAIN_NAME_LIST},"
    fi
    DOMAIN_NAME_LIST="${DOMAIN_NAME_LIST}${ADDITIONAL_SUBDOMAIN}.${THISDOMAINNAME}"
  fi
else
  echo "Existing domain name list already set"
fi


## Add CRON job to run monitorItemImport.pl
PREEXISTING_CRONJOB=`grep certbot /etc/crontab`

CRONJOB_SCRIPT="/usr/bin/certbot"
CRONJOB_LOGFILE="/var/log/letsencrypt-sslrenew.log"

RAND_MINUTE="$((2 + RANDOM % 57))"
RAND_HOUR="$((2 + RANDOM % 23))"

echo "RAND_MINUTE:             $RAND_MINUTE"
echo "RAND_HOUR:               $RAND_HOUR"

## line to add to crontab
if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]] || [[ "${REDHAT_RELEASE_DIGIT}" == "8" ]] || [[ "${REDHAT_RELEASE_DIGIT}" == "9" ]]; then
  CRONJOB_LINE="$RAND_MINUTE $RAND_HOUR * * * root certbot renew >> $CRONJOB_LOGFILE"
else
  CRONJOB_LINE="$RAND_MINUTE $RAND_HOUR * * * root /usr/bin/certbot renew >> $CRONJOB_LOGFILE"
fi

if [[ ${CONFIG_ENABLE_AUTORENEW} == "false" ]] ; then
  ## comment out the line if autorenew flag is false
  CRONJOB_LINE="## ${CRONJOB_LINE}"
fi

if [[ -e "$CRONJOB_SCRIPT" ]]; then
  if [[ "$PREEXISTING_CRONJOB" == "" ]]; then
    echo "Adding certbot renew:    /etc/crontab"
    echo "                         $CRONJOB_LINE"
    echo "Renewal output saved to: $CRONJOB_LOGFILE"
    echo ""

    ## add renewal cron job
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

## Check for /etc/httpd/conf.d/ssl.conf, comment it out if it exists
commentOutFile "/etc/httpd/conf.d" "ssl.conf"

# Enable httpd service at boot-time, and start httpd service
echo "Restarting service:      httpd"


if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  /sbin/chkconfig httpd --level 345 on || fail "chkconfig failed to enable httpd service"
  /sbin/service httpd restart || fail "failed to restart httpd service"
else
  /bin/systemctl daemon-reload
  /bin/systemctl enable httpd.service || fail "systemctl failed to enable httpd service"
  /bin/systemctl restart httpd || fail "failed to restart httpd service"
fi

CERTBOT_CMD="certbot --apache --agree-tos --email ${EMAIL_ADDR} -n -d ${DOMAIN_NAME_LIST}"

## save the command line and domain names used
SAVE_CMD_DIR="/usr/local/pbase-data/admin-only"
mkdir -p ${SAVE_CMD_DIR}

if [[ -e "${SAVE_CMD_DIR}/certbot-cmd.sh" ]] ; then
  echo "Saved command line:      ${SAVE_CMD_DIR}/certbot-cmd.sh"
else
  echo "Saving command line:     ${SAVE_CMD_DIR}/certbot-cmd.sh"
fi

echo ${CERTBOT_CMD} > ${SAVE_CMD_DIR}/certbot-cmd.sh


if [[ -e "${SAVE_CMD_DIR}/domain-name-list.txt" ]] ; then
  echo "Already saved domains:   ${SAVE_CMD_DIR}/domain-name-list.txt"
else
  echo "Saving domain name list: ${SAVE_CMD_DIR}/domain-name-list.txt"
  echo "Domain name list:        ${DOMAIN_NAME_LIST}"
  echo "${DOMAIN_NAME_LIST}" > ${SAVE_CMD_DIR}/domain-name-list.txt
fi

## show the domains to be registered
echo "                         $(cat ${SAVE_CMD_DIR}/domain-name-list.txt)"
echo ""

if [[ $EXECUTE_CERTBOT_CMD == "true" ]] ; then
  echo "Invoke certbot:          $CERTBOT_CMD"
  echo ""

  ## call Let's Encrypt to get SSL cert, will add file in /etc/httpd/conf...
  eval $CERTBOT_CMD

  if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
    /sbin/service httpd restart || fail "failed to restart httpd service"
  else
    /bin/systemctl restart httpd || fail "failed to restart httpd service"
  fi
else
  echo "Not invoking certbot:    $CERTBOT_CMD"
fi

echo ""
echo "Apache config files:     /etc/httpd/conf.d/"
ls -l /etc/httpd/conf.d/*.conf

append_bashrc_alias taillecronjoblog "tail -f $CRONJOB_LOGFILE"
append_bashrc_alias editcrontab "vi /etc/crontab"

%files
