Name: pbase-repo
Version: 1.0
Release: 0
Summary: PBase installer bootstrap rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-repo-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-repo
Requires: tar,which,wget,sed,grep,augeas

%description
Bootstrap rpm that adds YUM .repo file pointing to PBase repository

%prep
%setup -q

%install
mkdir -p "$RPM_BUILD_ROOT"
cp -R * "$RPM_BUILD_ROOT"

%clean
rm -rf "$RPM_BUILD_ROOT"

%pre
##echo "rpm preinstall $1"

## disable SELinux
ALREADY_DISABLED=$(grep "SELINUX=disabled" /etc/selinux/config)

if [[ "$ALREADY_DISABLED" == "" ]]; then
  echo "Disabling SELinux:       setenforce 0"
  setenforce 0

  if [ -f /etc/selinux/config ]; then
    # disable permanently
    echo "Configuring:             /etc/selinux/config:"
    echo "                         SELINUX=disabled"
    ## /bin/sed -i "s/SELINUX=enforcing/SELINUX=disabled/g" /etc/selinux/config

cat <<EOF | augtool --noautoload
set /augeas/load/Simplevars
set /augeas/load/Simplevars/lens "Simplevars.lns"
set /augeas/load/Simplevars/incl "/etc/selinux/config"
set /augeas/load/selinux/config
load
set /files/etc/selinux/config/SELINUX disabled
save
EOF

  fi
else
  echo "SE Linux already has:    $ALREADY_DISABLED"
fi

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

  ## Look for config .json file in one of two places.
  ##     /usr/local/pbase-data/admin-only/pbase_module_config.json
  ## or
  ##     /usr/local/pbase-data/admin-only/module-config.d/pbase_apache.json

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
  #else
  #  echo "Custom config not found: $PBASE_CONFIG"
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

service_exists() {
    local n=$1
    if [[ $(/bin/systemctl list-units --all -t service --full --no-legend "$n" | cut -f1 -d' ') == $n ]]; then
        return 0
    else
        return 1
    fi
}



echo ""
echo "PBase repository bootstrap rpm"

THISHOSTNAME="$(hostname)"
THISDOMAINNAME="$(hostname -d)"

check_linux_version

## look for config file "pbase_apache.json"
PBASE_CONFIG_FILENAME="pbase_repo.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
MODULE_SAMPLES_DIR="/usr/local/pbase-data/pbase-repo/module-config-samples"
PBASE_DEFAULTS_FILENAME="pbase_repo.json"

mkdir -p  ${MODULE_CONFIG_DIR}/
/bin/cp --no-clobber ${MODULE_SAMPLES_DIR}/${PBASE_CONFIG_FILENAME}  ${MODULE_CONFIG_DIR}/

echo "PBase config directory:  ${MODULE_SAMPLES_DIR}/"
echo ""
chmod 0600 ${MODULE_CONFIG_DIR}/
chmod 0600 ${MODULE_SAMPLES_DIR}/${PBASE_CONFIG_FILENAME}

## These defaults may be provided in text files at /root level
ROOT_DEFAULT_TEXTFILE_USED="false"
PBASE_REPO_JSON_PATH="/usr/local/pbase-data/admin-only/module-config.d/pbase_repo.json"

## use 'read' command to populate the default variables
DEFAULT_EMAIL_ADDRESS=""
DEFAULT_SMTP_SERVER=""
DEFAULT_SMTP_USERNAME=""
DEFAULT_SMTP_PASSWORD=""
DEFAULT_SUB_DOMAIN=""
DEFAULT_DESKTOP_USERNAME=""

if [[ -e /root/DEFAULT_EMAIL_ADDRESS.txt ]] ; then
  read -r DEFAULT_EMAIL_ADDRESS < /root/DEFAULT_EMAIL_ADDRESS.txt
fi

if [[ -e /root/DEFAULT_SMTP_SERVER.txt ]] ; then
  read -r DEFAULT_SMTP_SERVER < /root/DEFAULT_SMTP_SERVER.txt
fi

if [[ -e /root/DEFAULT_SMTP_USERNAME.txt ]] ; then
  read -r DEFAULT_SMTP_USERNAME < /root/DEFAULT_SMTP_USERNAME.txt
fi

if [[ -e /root/DEFAULT_SMTP_PASSWORD.txt ]] ; then
  read -r DEFAULT_SMTP_PASSWORD < /root/DEFAULT_SMTP_PASSWORD.txt
fi

## when subdomain text file exists, change 'null' literal to an empty string
## needed to do subdomain substitution later

if [[ -e /root/DEFAULT_SUB_DOMAIN.txt ]] ; then
  read -r DEFAULT_SUB_DOMAIN < /root/DEFAULT_SUB_DOMAIN.txt
  sed -i "s/defaultSubDomain\": null/defaultSubDomain\": \"\"/" ${PBASE_REPO_JSON_PATH}
fi

if [[ -e /root/DEFAULT_DESKTOP_USERNAME.txt ]] ; then
  read -r DEFAULT_DESKTOP_USERNAME < /root/DEFAULT_DESKTOP_USERNAME.txt
fi

## handle case where password is given, but smtp-username is empty. assume default smtp-username of 'postmaster@mail.example.com' typical for Mailgun
if [[ "${DEFAULT_SMTP_USERNAME}" == "" ]] && [[ "${DEFAULT_SMTP_PASSWORD}" != "" ]] ; then
  DEFAULT_SMTP_USERNAME="postmaster@mail.${THISDOMAINNAME}"
fi


## when a default was specified copy it to the json file used by other packages
## existing value may be either a json 'null' literal, or an empty string: ""

if [[ "${DEFAULT_EMAIL_ADDRESS}" != "" ]] ; then
  sed -i "s/defaultEmailAddress\": \"\"/defaultEmailAddress\": \"${DEFAULT_EMAIL_ADDRESS}\"/" ${PBASE_REPO_JSON_PATH}
  sed -i "s/defaultEmailAddress\": null/defaultEmailAddress\": \"${DEFAULT_EMAIL_ADDRESS}\"/" ${PBASE_REPO_JSON_PATH}
  echo "Reading:                 /root/DEFAULT_EMAIL_ADDRESS.txt"
  echo "defaultEmailAddress:     ${DEFAULT_EMAIL_ADDRESS}"
  ROOT_DEFAULT_TEXTFILE_USED="true"
fi

if [[ "${DEFAULT_SMTP_SERVER}" != "" ]] ; then
  sed -i "s/defaultSmtpServer\": \"\"/defaultSmtpServer\": \"${DEFAULT_SMTP_SERVER}\"/" ${PBASE_REPO_JSON_PATH}
  sed -i "s/defaultSmtpServer\": null/defaultSmtpServer\": \"${DEFAULT_SMTP_SERVER}\"/" ${PBASE_REPO_JSON_PATH}
  echo "Reading:                 /root/DEFAULT_SMTP_SERVER.txt"
  echo "defaultSmtpServer:       ${DEFAULT_SMTP_SERVER}"
  ROOT_DEFAULT_TEXTFILE_USED="true"
fi

if [[ "${DEFAULT_SMTP_USERNAME}" != "" ]] ; then
  sed -i "s/defaultSmtpUsername\": \"\"/defaultSmtpUsername\": \"${DEFAULT_SMTP_USERNAME}\"/" ${PBASE_REPO_JSON_PATH}
  sed -i "s/defaultSmtpUsername\": null/defaultSmtpUsername\": \"${DEFAULT_SMTP_USERNAME}\"/" ${PBASE_REPO_JSON_PATH}
  echo "Reading:                 /root/DEFAULT_SMTP_USERNAME.txt"
  echo "defaultSmtpUsername:     ${DEFAULT_SMTP_USERNAME}"
  ROOT_DEFAULT_TEXTFILE_USED="true"
fi

if [[ "${DEFAULT_SMTP_PASSWORD}" != "" ]] ; then
  sed -i "s/defaultSmtpPassword\": \"\"/defaultSmtpPassword\": \"${DEFAULT_SMTP_PASSWORD}\"/" ${PBASE_REPO_JSON_PATH}
  sed -i "s/defaultSmtpPassword\": null/defaultSmtpPassword\": \"${DEFAULT_SMTP_PASSWORD}\"/" ${PBASE_REPO_JSON_PATH}
  echo "Reading:                 /root/DEFAULT_SMTP_PASSWORD.txt"
  echo "defaultSmtpPassword:     ${DEFAULT_SMTP_PASSWORD}"
  ROOT_DEFAULT_TEXTFILE_USED="true"
fi

QT="'"
DEFAULT_SUB_DOMAIN_QUOTED=${QT}${DEFAULT_SUB_DOMAIN}${QT}

if [[ "${DEFAULT_SUB_DOMAIN}" != "" ]] ; then
  sed -i "s/defaultSubDomain\": \"\"/defaultSubDomain\": \"${DEFAULT_SUB_DOMAIN}\"/" ${PBASE_REPO_JSON_PATH}
  sed -i "s/defaultSubDomain\": null/defaultSubDomain\": \"${DEFAULT_SUB_DOMAIN}\"/" ${PBASE_REPO_JSON_PATH}
  echo "Reading:                 /root/DEFAULT_SUB_DOMAIN.txt"
  echo "defaultSubDomain:        ${DEFAULT_SUB_DOMAIN_QUOTED}"
  ROOT_DEFAULT_TEXTFILE_USED="true"
else
  if [[ -e /root/DEFAULT_SUB_DOMAIN.txt ]] ; then
    echo "Reading:                 /root/DEFAULT_SUB_DOMAIN.txt"
  fi
  echo "defaultSubDomain:        ${DEFAULT_SUB_DOMAIN_QUOTED}"
fi

if [[ "${DEFAULT_DESKTOP_USERNAME}" != "" ]] ; then
  sed -i "s/defaultDesktopUsername\": \"\"/defaultDesktopUsername\": \"${DEFAULT_DESKTOP_USERNAME}\"/" ${PBASE_REPO_JSON_PATH}
  sed -i "s/defaultDesktopUsername\": null/defaultDesktopUsername\": \"${DEFAULT_DESKTOP_USERNAME}\"/" ${PBASE_REPO_JSON_PATH}
  echo "Reading:                 /root/DEFAULT_DESKTOP_USERNAME.txt"
  echo "defaultDesktopUsername:  ${DEFAULT_DESKTOP_USERNAME}"
  ROOT_DEFAULT_TEXTFILE_USED="true"
fi


if [[ ${ROOT_DEFAULT_TEXTFILE_USED} == "true" ]] ; then
  echo ""
  echo "Updated default config:  ${PBASE_REPO_JSON_PATH}"
  echo ""
fi


## modify grub2 config file
export GRUB2_CONFIG_FILE="/etc/default/grub"

if [[ ! -e "${GRUB2_CONFIG_FILE}" ]]; then

    if [[ -e "/etc/system-release" ]]; then
       echo "grub2 not on version:    $(cat /etc/system-release)"
    fi
else
    echo "grub2 config file:       ${GRUB2_CONFIG_FILE}"
    export SEARCHFOR_TIMEOUT5="^GRUB_TIMEOUT=5"
    export REPLACESTR_TIMEOUT1="GRUB_TIMEOUT=1"

    if [[ -e ${GRUB2_CONFIG_FILE} ]]; then
        export ALREADY_HAS_TIMEOUT5=`grep ${SEARCHFOR_TIMEOUT5} ${GRUB2_CONFIG_FILE}`
        #echo "grub2 ALREADY_HAS_TIMEOUT5:  ${ALREADY_HAS_TIMEOUT5}"

        if [[ "${ALREADY_HAS_TIMEOUT5}" != "" ]]; then
            echo "Setting GRUB_TIMEOUT=1"

            sed -i "s/${SEARCHFOR_TIMEOUT5}/${REPLACESTR_TIMEOUT1}/" "${GRUB2_CONFIG_FILE}"

            echo "Regenerating grub2 boot-file"
            /sbin/grub2-mkconfig -o /boot/grub2/grub.cfg
        else
            echo "Already has grub2 modified GRUB_TIMEOUT value. Leaving unchanged."
        fi
    fi
fi


# Stop iptables/firewalld service

if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  echo "Disable iptables service"
  /sbin/service iptables stop
  chkconfig iptables off
else
  if service_exists firewalld.service; then
    echo "Disabling firewalld service - enable it after installing services"
    /bin/systemctl stop firewalld
    /bin/systemctl disable firewalld
  fi
fi


if [[ "$AMAZON1_RELEASE" != "" ]]; then
  echo "AMAZON1_RELEASE:         $AMAZON1_RELEASE"
elif [[ "$AMAZON2_RELEASE" != "" ]]; then
  echo "AMAZON2_RELEASE:         $AMAZON2_RELEASE"
fi


echo ""
echo "Enabling YUM repos:      /etc/yum.repos.d/"

if [[ "$AMAZON1_RELEASE" != "" ]]; then
  echo "AMZN1 Dependency repo:   pbase-amzn1-dep.repo"
  echo "EPEL repo:               epel.repo"
  /bin/cp -f /usr/local/pbase-data/pbase-repo/etc-yum-repos-d/amzn1/epel.repo /etc/yum.repos.d/
  /bin/cp -f /usr/local/pbase-data/pbase-repo/etc-yum-repos-d/amzn1/pbase-amzn1-dep.repo /etc/yum.repos.d/
elif [[ "$AMAZON2_RELEASE" != "" ]]; then
  echo "AMZN2 Dependency repo:   pbase-amzn2-dep.repo"
  echo "AMZN2 PHP 7.2 repo:      amzn2extra-php72.repo"
  /bin/cp -f /usr/local/pbase-data/pbase-repo/etc-yum-repos-d/amzn2/pbase-amzn2-dep.repo /etc/yum.repos.d/
  /bin/cp -f /usr/local/pbase-data/pbase-repo/etc-yum-repos-d/amzn2/amzn2extra-php72.repo /etc/yum.repos.d/
elif [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]] ; then
  echo "EL6 Dependency repo:     pbase-el6-dep.repo"
  /bin/cp -f /usr/local/pbase-data/pbase-repo/etc-yum-repos-d/el6/pbase-el6-dep.repo /etc/yum.repos.d/
elif [[ "${REDHAT_RELEASE_DIGIT}" == "7" ]] ; then
  echo "EL7 Dependency repo:     pbase-el7-dep.repo"
  /bin/cp -f /usr/local/pbase-data/pbase-repo/etc-yum-repos-d/el7/pbase-el7-dep.repo /etc/yum.repos.d/
elif [[ "${REDHAT_RELEASE_DIGIT}" == "8" ]] ; then
  echo "EL8 Dependency repo:     pbase-el8-dep.repo"
  /bin/cp -f /usr/local/pbase-data/pbase-repo/etc-yum-repos-d/el8/pbase-el8-dep.repo /etc/yum.repos.d/
elif [[ "${FEDORA_RELEASE}" != "" ]] ; then
  echo "Fedora Dependency repo:  pbase-fedora-dep.repo"
  /bin/cp -f /usr/local/pbase-data/pbase-repo/etc-yum-repos-d/fedora/pbase-fedora-dep.repo /etc/yum.repos.d/
else
  ## assume EL7 otherwise
  echo "EL7 Dependency repo:     pbase-el7-dep.repo"
  /bin/cp -f /usr/local/pbase-data/pbase-repo/etc-yum-repos-d/el7/pbase-el7-dep.repo /etc/yum.repos.d/
fi

echo ""

## Add aliases helpful for admin tasks to .bashrc
echo "" >> /root/.bashrc
append_bashrc_alias lltr "ls -ltr"
append_bashrc_alias ipaddr "ip addr | grep \"inet \""

if [[ "$FEDORA_RELEASE" != ""  ||  "${REDHAT_RELEASE_DIGIT}" == "8" ]]; then
  append_bashrc_alias tailyumlog "tail -f /var/log/dnf.log /var/log/dnf.rpm.log"
else
  append_bashrc_alias tailyumlog "tail -f -n100 /var/log/yum.log"
fi

echo ""
echo "PBase RPM repositories enabled "
echo ""

echo "Next steps - continue to install other pbase RPM modules"
echo "    The pbase-preconfig-* modules will place .json files in the directory:"
echo "        /usr/local/pbase-data/admin-only/module-config.d/"
echo "    ...  or samples to be copied to 'module-config.d' in:"
echo "        /usr/local/pbase-data/pbase-*/module-config-samples/"

if [[ ${ROOT_DEFAULT_TEXTFILE_USED} == "true" ]] ; then
  echo "    Populated from text files:  /root/DEFAULT_*"
  echo "        /usr/local/pbase-data/admin-only/module-config.d/pbase_repo.json"
else
  echo "Next step - optional - set the defaultEmailAddress in pbase_repo.json"
  echo "                       set the defaultSmtpServer for outgoing email"
  echo "                       set defaultSmtpPassword for outgoing email"
  echo "                       set defaultSubDomain to customize subdomain"
  echo "                       set defaultDesktopUsername for desktop app usage"
  echo ""
  echo "  cd /usr/local/pbase-data/admin-only/module-config.d"
  echo "  vi pbase_repo.json"
fi

echo ""

%preun
echo "rpm preuninstall"

## remove the repo files that were added by script
/bin/rm -f /etc/yum.repos.d/pbase-*-dep.repo


%files
## root only access to pbase configuration directories
%defattr(600,root,root,700)
/etc/yum.repos.d/pbase.repo
/usr/local/pbase-data/pbase-repo/etc-yum-repos-d/amzn1/epel.repo
/usr/local/pbase-data/pbase-repo/etc-yum-repos-d/amzn1/pbase-amzn1-dep.repo
/usr/local/pbase-data/pbase-repo/etc-yum-repos-d/amzn2/epel.repo
/usr/local/pbase-data/pbase-repo/etc-yum-repos-d/amzn2/pbase-amzn2-dep.repo
/usr/local/pbase-data/pbase-repo/etc-yum-repos-d/amzn2/amzn2extra-php72.repo
/usr/local/pbase-data/pbase-repo/etc-yum-repos-d/el6/epel.repo
/usr/local/pbase-data/pbase-repo/etc-yum-repos-d/el7/epel.repo
/usr/local/pbase-data/pbase-repo/etc-yum-repos-d/el8/epel.repo
/usr/local/pbase-data/pbase-repo/etc-yum-repos-d/el6/pbase-el6-dep.repo
/usr/local/pbase-data/pbase-repo/etc-yum-repos-d/el7/pbase-el7-dep.repo
/usr/local/pbase-data/pbase-repo/etc-yum-repos-d/el8/pbase-el8-dep.repo
/usr/local/pbase-data/pbase-repo/etc-yum-repos-d/fedora/pbase-fedora-dep.repo
/usr/local/pbase-data/pbase-repo/etc-pki-rpm-gpg/RPM-GPG-KEY-EPEL-6
/usr/local/pbase-data/pbase-repo/etc-pki-rpm-gpg/RPM-GPG-KEY-EPEL-7
/usr/local/pbase-data/pbase-repo/etc-pki-rpm-gpg/RPM-GPG-KEY-EPEL-8
/usr/local/pbase-data/pbase-repo/module-config-samples/pbase_repo.json