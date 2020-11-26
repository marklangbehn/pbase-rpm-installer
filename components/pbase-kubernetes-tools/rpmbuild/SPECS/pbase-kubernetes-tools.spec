Name: pbase-kubernetes-tools
Version: 1.0
Release: 0
Summary: PBase Kubernetes Tools
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot 

Provides: pbase-kubernetes-tools
Requires: pbase-kvm, wget, curl, jq

%description
PBase Kubernetes Tools Install

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

echo "PBase Kubernetes Tools Install"
echo ""

MODULE_CONFIG_DIR="/usr/local/pbase-data/admin-only/module-config.d"
PBASE_DEFAULTS_FILENAME="pbase_repo.json"

## look for either separate config file like "pbase_repo.json" or all-in-one file: "pbase_module_config.json"
PBASE_CONFIG_FILENAME="$PBASE_DEFAULTS_FILENAME"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config values from JSON file
parseConfig "DEFAULT_DESKTOP_USER_NAME" ".pbase_repo.defaultDesktopUsername" ""

DESKTOP_USER_NAME="mydesktopusername"
if [[ "$DEFAULT_DESKTOP_USER_NAME" != "" ]]; then
  echo "defaultDesktopUsername:  $DEFAULT_DESKTOP_USER_NAME"
  DESKTOP_USER_NAME="$DEFAULT_DESKTOP_USER_NAME"
fi

## download minikube and place it /usr/local/bin
cd /tmp
wget -q https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
chmod +x minikube-linux-amd64
mv minikube-linux-amd64 /usr/local/bin/minikube

## download kubectl command line tool and place it /usr/local/bin
cd /tmp
curl -s -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl
chmod +x kubectl
mv kubectl  /usr/local/bin/

## show kubectl info
## /usr/local/bin/kubectl version --client -o json



## set permission for desktop user
if [[ "$DEFAULT_DESKTOP_USER_NAME" != "" ]]; then
  echo "Setting ownership:       usermod -a -G libvirt $DEFAULT_DESKTOP_USER_NAME"
  usermod -a -G libvirt $DEFAULT_DESKTOP_USER_NAME
fi

echo "Next step:               Install a KVM 'driver' such as:"
echo "                         docker, podman, virtualbox, vmware"
echo ""
echo "Next step - if needed - as root, add your desktop username to KVM 'libvirt' group:"
echo "  usermod -a -G libvirt $DESKTOP_USER_NAME"
echo ""
echo "Once your desktop user has been set you can run minikube as that user:"
echo "  minikube status"
echo "...or"
echo "  minikube dashboard"
echo ""

echo "The 'kubectl' command-line utility is also installed:"
echo "  kubectl get nodes"
echo "...show kubectl info with this command:"
echo "  kubectl version --client -o json"
echo ""

%files
