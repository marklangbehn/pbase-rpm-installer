Name: pbase-docker-ce
Version: 1.0
Release: 0
Summary: PBase Docker CE and Docker Compose installation
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot 

Provides: pbase-docker-ce
Requires: docker-ce, docker-ce-cli, containerd.io, jq

%description
Docker CE and Docker Compose installation

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

echo "PBase Docker CE and Docker Compose installation"

## config is stored in json file with root-only permissions
## it can be one of two places:
##     /usr/local/pbase-data/admin-only/pbase_module_config.json
## or
##     /usr/local/pbase-data/admin-only/module-config.d/pbase_docker_ce.json

locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_docker_ce.json"
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


## look for either separate config file "pbase_docker_ce.json" or all-in-one file: "pbase_module_config.json"
PBASE_CONFIG_FILENAME="pbase_docker_ce.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "ADD_USER_TO_DOCKER_GRP" ".pbase_docker_ce.addUserToDockerGroup" ""

echo "ADD_USER_TO_DOCKER_GRP:  $ADD_USER_TO_DOCKER_GRP"

REQUESTED_USER_EXISTS=$(grep "^${ADD_USER_TO_DOCKER_GRP}\\:" /etc/passwd)
##echo "REQUESTED_USER_EXISTS:   $REQUESTED_USER_EXISTS"

if [[ $REQUESTED_USER_EXISTS != "" ]] && [[ $ADD_USER_TO_DOCKER_GRP != "" ]] ; then

  echo "Executing:               usermod -aG docker $ADD_USER_TO_DOCKER_GRP"
  usermod -aG docker $ADD_USER_TO_DOCKER_GRP
fi

## Add aliases helpful for admin tasks to .bashrc
echo "" >> /root/.bashrc

append_bashrc_alias taildocker "journalctl -fu docker.service"

append_bashrc_alias stopdocker "/bin/systemctl stop docker"
append_bashrc_alias startdocker "/bin/systemctl start docker"
append_bashrc_alias statusdocker "/bin/systemctl status docker"
append_bashrc_alias restartdocker "/bin/systemctl restart docker"

echo "Starting docker service"
echo ""

/bin/systemctl daemon-reload
/bin/systemctl enable docker.service || fail "systemctl failed to enable docker service"
/bin/systemctl restart docker || fail "failed to restart docker service"
/bin/systemctl status docker || fail "failed to restart docker service"

echo ""

%files
