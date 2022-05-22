Name: pbase-preconfig-elasticsearch
Version: 1.0
Release: 1
Summary: PBase Elasticsearch repo preconfigure
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-elasticsearch-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-elasticsearch

%description
Configure yum repo for Elasticsearch

%prep
%setup -q

%install
mkdir -p "$RPM_BUILD_ROOT"
cp -R * "$RPM_BUILD_ROOT"

%clean
rm -rf "$RPM_BUILD_ROOT"

%pre

%post
echo "rpm postinstall $1"

fail() {
    echo "ERROR: $1"
    exit 1
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

echo "PBase Elasticsearch repo pre-configuration"

## check which version of Linux is installed
check_linux_version

if [[ -e "/etc/yum.repos.d/elasticsearch.repo" ]]; then
  echo "Existing elasticsearch.repo found, leaving unchanged"
elif [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  echo "Elasticsearch el6:       NOT SUPPORTED"
  ##TODO error exit
  ## /bin/cp -f /usr/local/pbase-data/pbase-preconfig-elasticsearch/etc-yum-repos-d/el6/elasticsearch.repo /etc/yum.repos.d/elasticsearch.repo
else
  echo "Elasticsearch el7:       /etc/yum.repos.d/elasticsearch.repo"
  /bin/cp -f /usr/local/pbase-data/pbase-preconfig-elasticsearch/etc-yum-repos-d/el7/elasticsearch.repo /etc/yum.repos.d/elasticsearch.repo

  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig-elasticsearch/etc-pki-rpm-gpg/GPG-KEY-elasticsearch /etc/pki/rpm-gpg
fi

## TODO check for java

echo ""
echo "Elasticsearch repo configured."
echo "Next step - optional - change the Elasticsearch server default config by"
echo "     making a copy of the sample file, and editing it. For example:"
echo ""

echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  cp /usr/local/pbase-data/pbase-preconfig-elasticsearch/module-config-samples/pbase_elasticsearch.json ."
echo "  vi pbase_elasticsearch.json"

echo ""
echo "Next step - install elasticsearch service with:"
echo "  yum install pbase-elasticsearch"

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-elasticsearch/etc-yum-repos-d/el7/elasticsearch.repo
/usr/local/pbase-data/pbase-preconfig-elasticsearch/etc-pki-rpm-gpg/GPG-KEY-elasticsearch
/usr/local/pbase-data/pbase-preconfig-elasticsearch/module-config-samples/pbase_elasticsearch.json
