Name: pbase-elasticsearch
Version: 1.0
Release: 0
Summary: PBase Elasticsearch server rpm
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-elasticsearch
Requires: elasticsearch = 6.4.2,curl,jq

%description
Install Elasticsearch server

%prep

%install
#mkdir -p "$RPM_BUILD_ROOT"
#cp -R * "$RPM_BUILD_ROOT"

%clean
#rm -rf "$RPM_BUILD_ROOT"

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


echo "PBase Elasticsearch server"

## config is stored in json file with root-only permissions
##     /usr/local/pbase-data/admin-only/module-config.d/pbase_elasticsearch.json


locateConfigFile() {
  ## name of config file is passed in param $1 - for example "pbase_elasticsearch.json"
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


## look for config file "pbase_elasticsearch.json"
PBASE_CONFIG_FILENAME="pbase_elasticsearch.json"

locateConfigFile "$PBASE_CONFIG_FILENAME"

## fetch config value from JSON file
parseConfig "CONFIG_ES_NODE_MASTER" ".pbase_elasticsearch.node_master" "false"
parseConfig "CONFIG_ES_NODE_NAME" ".pbase_elasticsearch.node_name" "esnode-1"
parseConfig "CONFIG_ES_CLUSTER_NAME" ".pbase_elasticsearch.cluster_name" "esmy-application"

echo "CONFIG_ES_NODE_MASTER:   $CONFIG_ES_NODE_MASTER"
echo "CONFIG_ES_NODE_NAME:     $CONFIG_ES_NODE_NAME"
echo "CONFIG_ES_CLUSTER_NAME:  $CONFIG_ES_CLUSTER_NAME"


## Get hostname to be substituted in template config files
THISHOSTNAME="$(hostname)"
TMPLHOSTNAME="fiver.emosonic.com"


## Default config - open access for 'my-application'
ES_CONFIG_YML="/etc/elasticsearch/elasticsearch.yml"
echo "Updating config file:    ${ES_CONFIG_YML}"


#sed -i "s/#cluster.name: my-application/cluster.name: my-application/" $ES_CONFIG_YML
#sed -i "s/#node.name: node-1/node.name: node-1/" $ES_CONFIG_YML
#sed -i "s/#network.host: 192.168.0.1/network.host: 0.0.0.0/" $ES_CONFIG_YML

sed -i "s/#cluster.name: my-application/cluster.name: $CONFIG_ES_CLUSTER_NAME/" $ES_CONFIG_YML
sed -i "s/#node.name: node-1/node.name: $CONFIG_ES_NODE_NAME/" $ES_CONFIG_YML
sed -i "s/#network.host: 192.168.0.1/network.host: 0.0.0.0/" $ES_CONFIG_YML



## check which version of Linux is installed
check_linux_version


# Start and enable elasticsearch service at boot-time

if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  /sbin/service elasticsearch stop
else
  /bin/systemctl stop elasticsearch
fi

# Start and enable elasticsearch service at boot-time

if [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  /sbin/chkconfig elasticsearch --level 345 on || fail "chkconfig failed to enable elasticsearch service"
  /sbin/service elasticsearch start || fail "failed to restart elasticsearch service"
else
  /bin/systemctl daemon-reload
  /bin/systemctl enable elasticsearch.service || fail "systemctl failed to enable elasticsearch service"
  /bin/systemctl start elasticsearch || fail "failed to restart elasticsearch service"
  /bin/systemctl status elasticsearch

  echo "To check status:         curl http://localhost:9200"
fi


## Add aliases helpful for admin tasks to .bashrc
echo "" >> /root/.bashrc
append_bashrc_alias tailelastic "tail -f -n100 /var/log/elasticsearch/${CONFIG_ES_CLUSTER_NAME}.log"

if [[ "$REDHAT_RELEASE_DIGIT" == "6" ]]; then
  append_bashrc_alias stopelastic "service elasticsearch stop"
  append_bashrc_alias startelastic "service elasticsearch start"
  append_bashrc_alias statuselastic "service elasticsearch status"
  append_bashrc_alias restartelastic "service elasticsearch restart"
else
  append_bashrc_alias stopelastic "/bin/systemctl stop elasticsearch"
  append_bashrc_alias startelastic "/bin/systemctl start elasticsearch"
  append_bashrc_alias statuselastic "/bin/systemctl status elasticsearch"
  append_bashrc_alias restartelastic "/bin/systemctl restart elasticsearch"
fi

echo " "

%files
