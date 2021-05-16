Name: pbase-kvm
Version: 1.0
Release: 1
Summary: PBase KVM Hypervisor Install
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-kvm
Requires: pbase-epel, libvirt qemu-kvm, virt-install, virt-top, libguestfs-tools

%description
PBase KVM Hypervisor Install

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

## config is stored in json file with root-only permissions
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

echo "PBase KVM Hypervisor Install"

if [[ $1 -ne 1 ]] ; then
  echo "Already Installed. Exiting."
  exit 0
fi

echo ""

MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
PBASE_DEFAULTS_FILENAME="pbase_repo.json"

## look for config file like "pbase_repo.json"
PBASE_CONFIG_FILENAME="$PBASE_DEFAULTS_FILENAME"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config values from JSON file
parseConfig "DEFAULT_DESKTOP_USER_NAME" ".pbase_repo.defaultDesktopUsername" ""

DESKTOP_USER_NAME="mydesktopusername"
if [[ "$DEFAULT_DESKTOP_USER_NAME" != "" ]] && [[ "$DEFAULT_DESKTOP_USER_NAME" != null ]]; then
  DESKTOP_USER_NAME="$DEFAULT_DESKTOP_USER_NAME"
fi

echo "defaultDesktopUsername:  $DESKTOP_USER_NAME"

## set permission for desktop user
if [[ "$DESKTOP_USER_NAME" != "" ]] && [[ "$DESKTOP_USER_NAME" != "null" ]] && [[ "$DESKTOP_USER_NAME" != "mydesktopusername" ]] ; then
  echo "Setting ownership:       usermod -a -G libvirt $DESKTOP_USER_NAME"
  usermod -a -G libvirt $DESKTOP_USER_NAME
fi

echo "Starting service:        libvirtd"

systemctl daemon-reload
systemctl enable libvirtd
systemctl start libvirtd

echo ""
echo "Enabling libvirt group:  /etc/libvirt/libvirtd.conf"

sed -i "s/^#unix_sock_group/unix_sock_group/" /etc/libvirt/libvirtd.conf
sed -i "s/^#unix_sock_ro_perms/unix_sock_ro_perms/" /etc/libvirt/libvirtd.conf

## restart after permissions set
systemctl restart libvirtd
systemctl status libvirtd

echo "Next step - if needed - as root, add your desktop username to KVM 'libvirt' group:"
echo ""
echo "  usermod -a -G libvirt $DESKTOP_USER_NAME"
echo ""

%files
