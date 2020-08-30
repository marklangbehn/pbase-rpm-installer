Name: pbase-preconfig-rpmfusion
Version: 1.0
Release: 0
Summary: RPMFusion repo preconfigure
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: pbase-preconfig-rpmfusion-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-preconfig-rpmfusion
## Requires:

%description
Configure yum repo for RPMFusion

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


echo "Multimedia RPMFusion repo pre-configuration"
echo ""


## check which version of Linux is installed
check_linux_version


if [[ "${REDHAT_RELEASE_DIGIT}" == "8" ]]; then
  YUM_REPO_PATH1="/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-yum-repos-d/el8/rpmfusion-free-updates.repo"
  YUM_REPO_PATH2="/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-yum-repos-d/el8/rpmfusion-nonfree-updates.repo"

  /bin/cp -f $YUM_REPO_PATH1 /etc/yum.repos.d/
  /bin/cp -f $YUM_REPO_PATH2 /etc/yum.repos.d/

  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-pki-rpm-gpg/el8/RPM-GPG-KEY-rpmfusion-free-el-8  /etc/pki/rpm-gpg/
  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-pki-rpm-gpg/el8/RPM-GPG-KEY-rpmfusion-nonfree-el-8  /etc/pki/rpm-gpg/
elif [[ "${REDHAT_RELEASE_DIGIT}" == "6" ]]; then
  YUM_REPO_PATH1="/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-yum-repos-d/el6/rpmfusion-free-updates.repo"
  YUM_REPO_PATH2="/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-yum-repos-d/el6/rpmfusion-nonfree-updates.repo"

  /bin/cp -f $YUM_REPO_PATH1 /etc/yum.repos.d/
  /bin/cp -f $YUM_REPO_PATH2 /etc/yum.repos.d/

  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-pki-rpm-gpg/el6/RPM-GPG-KEY-rpmfusion-free-el-6  /etc/pki/rpm-gpg/
  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-pki-rpm-gpg/el6/RPM-GPG-KEY-rpmfusion-nonfree-el-6  /etc/pki/rpm-gpg/
elif [[ "$FEDORA_RELEASE" != "" ]]; then
  YUM_REPO_PATH1="/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-yum-repos-d/fedora/rpmfusion-free.repo"
  YUM_REPO_PATH2="/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-yum-repos-d/fedora/rpmfusion-free-updates.repo"
  YUM_REPO_PATH3="/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-yum-repos-d/fedora/rpmfusion-nonfree.repo"
  YUM_REPO_PATH4="/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-yum-repos-d/fedora/rpmfusion-nonfree-updates.repo"

  /bin/cp -f --no-clobber $YUM_REPO_PATH1 /etc/yum.repos.d/
  /bin/cp -f --no-clobber $YUM_REPO_PATH2 /etc/yum.repos.d/
  /bin/cp -f --no-clobber $YUM_REPO_PATH3 /etc/yum.repos.d/
  /bin/cp -f --no-clobber $YUM_REPO_PATH4 /etc/yum.repos.d/

  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-pki-rpm-gpg/el7/RPM-GPG-KEY-rpmfusion-free-el-7  /etc/pki/rpm-gpg/
  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-pki-rpm-gpg/el7/RPM-GPG-KEY-rpmfusion-nonfree-el-7  /etc/pki/rpm-gpg/
else
  YUM_REPO_PATH1="/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-yum-repos-d/el7/rpmfusion-free-updates.repo"
  YUM_REPO_PATH2="/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-yum-repos-d/el7/rpmfusion-nonfree-updates.repo"

  /bin/cp -f $YUM_REPO_PATH1 /etc/yum.repos.d/
  /bin/cp -f $YUM_REPO_PATH2 /etc/yum.repos.d/

  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-pki-rpm-gpg/el7/RPM-GPG-KEY-rpmfusion-free-el-7  /etc/pki/rpm-gpg/
  /bin/cp -f --no-clobber /usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-pki-rpm-gpg/el7/RPM-GPG-KEY-rpmfusion-nonfree-el-7  /etc/pki/rpm-gpg/
fi


if [[ -e "/etc/yum.repos.d/rpmfusion-free-updates.repo" ]]; then
  echo "Existing YUM repo:       /etc/yum.repos.d/rpmfusion-free-updates.repo"
else
  echo "rpmfusion-free-updates:  /etc/yum.repos.d/rpmfusion-free-updates.repo"
  /bin/cp -f $YUM_REPO_PATH /etc/yum.repos.d/
  /bin/cp -f $YUM_REPO_PATH2 /etc/yum.repos.d/
fi

echo ""
echo "RPMFusion repo configured."
echo "Next step - install multimedia codec with:"
echo ""
echo "  yum -y install gstreamer1-libav gstreamer1-plugins-good gstreamer1-plugins-bad-free gstreamer1-plugins-bad-freeworld gstreamer1-plugins-bad-nonfree gstreamer1-plugins-ugly"


echo ""
echo "Next step - install multimedia apps such as:"
echo ""
echo "  yum -y install ffmpeg vlc"
echo ""


%preun
echo "rpm preuninstall"

## remove the repo files that were added by script
/bin/rm -f /etc/yum.repos.d/rpmfusion-*.repo

%files
%defattr(600,root,root,700)
/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-yum-repos-d/el6/rpmfusion-free-updates.repo
/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-yum-repos-d/el6/rpmfusion-nonfree-updates.repo

/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-yum-repos-d/el7/rpmfusion-free-updates.repo
/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-yum-repos-d/el7/rpmfusion-nonfree-updates.repo

/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-yum-repos-d/el8/rpmfusion-free-updates.repo
/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-yum-repos-d/el8/rpmfusion-nonfree-updates.repo

/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-yum-repos-d/fedora/rpmfusion-free.repo
/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-yum-repos-d/fedora/rpmfusion-nonfree.repo
/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-yum-repos-d/fedora/rpmfusion-free-updates.repo
/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-yum-repos-d/fedora/rpmfusion-nonfree-updates.repo

/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-pki-rpm-gpg/el6/RPM-GPG-KEY-rpmfusion-free-el-6
/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-pki-rpm-gpg/el6/RPM-GPG-KEY-rpmfusion-nonfree-el-6

/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-pki-rpm-gpg/el7/RPM-GPG-KEY-rpmfusion-free-el-7
/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-pki-rpm-gpg/el7/RPM-GPG-KEY-rpmfusion-nonfree-el-7

/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-pki-rpm-gpg/el8/RPM-GPG-KEY-rpmfusion-free-el-8
/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-pki-rpm-gpg/el8/RPM-GPG-KEY-rpmfusion-nonfree-el-8

/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-pki-rpm-gpg/fedora/RPM-GPG-KEY-rpmfusion-free-fedora-30
/usr/local/pbase-data/pbase-preconfig-rpmfusion/etc-pki-rpm-gpg/fedora/RPM-GPG-KEY-rpmfusion-nonfree-fedora-30
