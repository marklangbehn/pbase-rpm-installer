Name: pbase-preconfig
Version: 1.0
Release: 0
Summary: PBase installer bootstrap rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig
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
echo "rpm preinstall $1"

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


## config is stored in json file with root-only permsissions
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


echo ""
echo "PBase bootstrap preconfig"

check_linux_version

## look for either separate config file "pbase_apache.json" or all-in-one file: "pbase_module_config.json"
PBASE_CONFIG_FILENAME="pbase_preconfig.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"


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
  #/bin/systemctl stop iptables.service
  #/bin/systemctl disable iptables.service
  echo "Disable firewalld service"

  /bin/systemctl stop firewalld
  /bin/systemctl disable firewalld
fi


if [[ "$AMAZON1_RELEASE" != "" ]]; then
  echo "AMAZON1_RELEASE:         $AMAZON1_RELEASE"
elif [[ "$AMAZON2_RELEASE" != "" ]]; then
  echo "AMAZON2_RELEASE:           $AMAZON2_RELEASE"
fi


echo ""
echo "Enabling YUM repos:      /etc/yum.repos.d/"

## don't add EPEL if running on Fedora, or if already exists

if [[ -e "/etc/yum.repos.d/epel.repo" ]]; then
  if [[ "$AMAZON1_RELEASE" != "" ]]; then
    echo "epel for Amazon Linux 1: yum-config-manager --enable epel"
    yum-config-manager --enable epel
  else
    echo "Existing EPEL repo:      leaving unchanged"
  fi

elif [[ "$AMAZON2_RELEASE" != "" ]]; then
  echo "epel for Amazon Linux 2: /etc/yum.repos.d/epel.repo"
  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/amzn2/epel.repo /etc/yum.repos.d/
  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig/etc-pki-rpm-gpg/RPM-GPG-KEY-EPEL-7 /etc/pki/rpm-gpg/

elif [[ "$FEDORA_RELEASE" == "" ]]; then

  if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
    echo "epel for EL6:            /etc/yum.repos.d/epel.repo"
    /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/el6/epel.repo /etc/yum.repos.d/
    /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig/etc-pki-rpm-gpg/RPM-GPG-KEY-EPEL-6 /etc/pki/rpm-gpg

  elif [[ "${REDHAT_RELEASE_DIGIT}" == "7" ]]; then
    echo "epel for EL7:            /etc/yum.repos.d/epel.repo"
    /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/el7/epel.repo /etc/yum.repos.d/
    /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig/etc-pki-rpm-gpg/RPM-GPG-KEY-EPEL-7 /etc/pki/rpm-gpg

  elif [[ "${REDHAT_RELEASE_DIGIT}" == "8" ]]; then
    echo "epel for EL8:            /etc/yum.repos.d/epel.repo"
    /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/el8/epel.repo /etc/yum.repos.d/
    /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig/etc-pki-rpm-gpg/RPM-GPG-KEY-EPEL-8 /etc/pki/rpm-gpg
  fi
fi


if [[ "$AMAZON1_RELEASE" != "" ]]; then
  echo "AMZN1 Dependency repo:   pbase-amzn1-dep.repo"
  /bin/cp -f /usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/amzn1/pbase-amzn1-dep.repo /etc/yum.repos.d/
elif [[ "$AMAZON2_RELEASE" != "" ]]; then
  echo "AMZN2 Dependency repo:   pbase-amzn2-dep.repo"
  /bin/cp -f /usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/amzn2/pbase-amzn2-dep.repo /etc/yum.repos.d/
elif [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]] ; then
  echo "EL6 Dependency repo:     pbase-el6-dep.repo"
  /bin/cp -f /usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/el6/pbase-el6-dep.repo /etc/yum.repos.d/
elif [[ "${REDHAT_RELEASE_DIGIT}" == "7" ]] ; then
  echo "EL7 Dependency repo:     pbase-el7-dep.repo"
  /bin/cp -f /usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/el7/pbase-el7-dep.repo /etc/yum.repos.d/
elif [[ "${REDHAT_RELEASE_DIGIT}" == "8" ]] ; then
  echo "EL8 Dependency repo:     pbase-el8-dep.repo"
  /bin/cp -f /usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/el8/pbase-el8-dep.repo /etc/yum.repos.d/
elif [[ "${FEDORA_RELEASE}" != "" ]] ; then
  echo "Fedora Dependency repo:     pbase-fedora-dep.repo"
  /bin/cp -f /usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/fedora/pbase-fedora-dep.repo /etc/yum.repos.d/
else
  ## assume EL7 otherwise
  echo "EL7 Dependency repo:     pbase-el7-dep.repo"
  /bin/cp -f /usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/el7/pbase-el7-dep.repo /etc/yum.repos.d/
fi

echo ""

## add aliases
echo "" >> /root/.bashrc
append_bashrc_alias lltr "ls -ltr"
append_bashrc_alias ipaddr "ip addr | grep \"inet \""

if [[ "$FEDORA_RELEASE" != ""  ||  "${REDHAT_RELEASE_DIGIT}" == "8" ]]; then
  append_bashrc_alias tailyumlog "tail -f /var/log/dnf.log /var/log/dnf.rpm.log"
else
  append_bashrc_alias tailyumlog "tail -f -n100 /var/log/yum.log"
fi

echo ""
echo "The PBase RPM modules' configuration can be customized with a JSON file "
echo ""

echo "Next steps - option #1 - Customize the configuration with JSON files for specifc"
echo "    PBase RPM modules by simply making a copy of a sample file and editing it."
echo "    Many of the PBase RPMs place a sample JSON file in the directory:"
echo "        /usr/local/pbase-data/admin-only/module-config-samples/"
echo ""
echo "    For example: the pbase-apache module would be customized by:"
echo ""
echo "    yum -y install pbase-preconfig-apache"
echo "    cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "    cp ../module-config-samples/pbase_apache.json ."
echo "    vi pbase_apache.json"
echo ""
echo "    After that file has been edited complete the install with:"
echo "    yum -y install pbase-apache"

echo ""
echo "Next steps - option #2 - Use the default configurations provided by the RPMs."
echo "    This is intended for development workstations or demo servers "
echo "    that can be configured afterwards if needed."
echo ""


%preun
echo "rpm preuninstall"

## remove the repo files that were added by script
/bin/rm -f /etc/yum.repos.d/pbase-*-dep.repo


%files
## root only access to pbase configuration directories
%defattr(600,root,root,700)
/etc/yum.repos.d/pbase.repo
/usr/local/pbase-data/admin-only/module-config.d
/usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/amzn1/epel.repo
/usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/amzn1/pbase-amzn1-dep.repo
/usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/amzn2/epel.repo
/usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/amzn2/pbase-amzn2-dep.repo
/usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/amzn2/amzn2extra-php72.repo
/usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/el6/epel.repo
/usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/el7/epel.repo
/usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/el8/epel.repo
/usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/el6/pbase-el6-dep.repo
/usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/el7/pbase-el7-dep.repo
/usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/el8/pbase-el8-dep.repo
/usr/local/pbase-data/pbase-preconfig/etc-yum-repos-d/fedora/pbase-fedora-dep.repo
/usr/local/pbase-data/pbase-preconfig/etc-pki-rpm-gpg/RPM-GPG-KEY-EPEL-6
/usr/local/pbase-data/pbase-preconfig/etc-pki-rpm-gpg/RPM-GPG-KEY-EPEL-7
/usr/local/pbase-data/pbase-preconfig/etc-pki-rpm-gpg/RPM-GPG-KEY-EPEL-8
/usr/local/pbase-data/admin-only/module-config.d/
/usr/local/pbase-data/admin-only/module-config-samples/pbase_preconfig.json
