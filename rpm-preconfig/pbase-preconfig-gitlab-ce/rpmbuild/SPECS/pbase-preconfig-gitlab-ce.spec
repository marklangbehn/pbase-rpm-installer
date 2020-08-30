Name: pbase-preconfig-gitlab-ce
Version: 1.0
Release: 0
Summary: PBase GitLab CE repo preconfigure
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-gitlab-ce-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-gitlab-ce
Requires: curl, policycoreutils, openssh-server, python3-policycoreutils

%description
Configure yum repo and dependencies for current GitLab CE version

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


echo "PBase GitLab CE yum repos and dependencies pre-configuration"
echo ""

## check which version of Linux is installed
check_linux_version

## default repo path
YUM_REPO_PATH="/usr/local/pbase-data/pbase-preconfig-gitlab-ce/etc-yum-repos-d/el8/gitlab_gitlab-ce.repo"

## /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig-gitlab-ce/etc-pki-rpm-gpg/gitlab-ce-gpg  /etc/pki/rpm-gpg

if [[ -e "/etc/yum.repos.d/gitlab_gitlab-ce.repo" ]] ; then
  echo "Existing YUM repo:       /etc/yum.repos.d/gitlab_gitlab-ce.repo"
else
  if [[ "$FEDORA_RELEASE" != "" ]] ; then
    echo "gitlab-ce for Fedora"
    YUM_REPO_PATH="/usr/local/pbase-data/pbase-preconfig-gitlab-ce/etc-yum-repos-d/fedora/gitlab_gitlab-ce.repo"
  elif [[ "$REDHAT_RELEASE_DIGIT" == "6" ]] ; then
    echo "gitlab-ce for EL6 not available"
    return 1
  elif [[ "$REDHAT_RELEASE_DIGIT" == "7" ]] ; then
    echo "gitlab-ce for EL7"
    YUM_REPO_PATH="/usr/local/pbase-data/pbase-preconfig-gitlab-ce/etc-yum-repos-d/el7/gitlab_gitlab-ce.repo"
  elif [[ "$REDHAT_RELEASE_DIGIT" == "8" ]] ; then
    echo "gitlab-ce for EL8"
    YUM_REPO_PATH="/usr/local/pbase-data/pbase-preconfig-gitlab-ce/etc-yum-repos-d/el8/gitlab_gitlab-ce.repo"
  fi

  echo "gitlab_gitlab-ce.repo:          /etc/yum.repos.d/gitlab_gitlab-ce.repo"
  /bin/cp -f $YUM_REPO_PATH /etc/yum.repos.d/
fi


echo ""
echo "GitLab CE repo configured."
echo "Next step - change the default GitLab setup by making"
echo "     a copy of the config sample file and editing it. For example:"
echo ""

echo "  cd /usr/local/pbase-data/admin-only/module-config.d/"
echo "  cp ../module-config-samples/pbase_gitlab_ce.json ."
echo "  vi pbase_gitlab_ce.json"

echo ""
echo "Next step - install GitLab CE with:"
echo "  yum -y install pbase-gitlab-ce"
echo ""

%preun
echo "rpm preuninstall"

## remove the repo file added by script
/bin/rm -f /etc/yum.repos.d/gitlab_gitlab-ce.repo


%files
## root only access to pbase configuration directories
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-gitlab-ce/etc-yum-repos-d/el7/gitlab_gitlab-ce.repo
/usr/local/pbase-data/pbase-preconfig-gitlab-ce/etc-yum-repos-d/el8/gitlab_gitlab-ce.repo
/usr/local/pbase-data/pbase-preconfig-gitlab-ce/etc-yum-repos-d/fedora/gitlab_gitlab-ce.repo
/usr/local/pbase-data/admin-only/module-config-samples/pbase_gitlab_ce.json
