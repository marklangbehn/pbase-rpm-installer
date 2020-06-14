Name: pbase-php-amzn2-dep
Version: 1.0
Release: 0
Summary: PBase PHP 7 transitive dependencies for Amazon Linux 2
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

Provides: pbase-php-transitive-dep

%description
PBase PHP 7.2 transitive dependencies for Amazon Linux 2

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

echo "PBase PHP 7.2 transitive dependencies for Amazon Linux 2"

ALREADY_HAS_XTRAS_PHP72=$(grep "amzn2extra-php7.2" "/etc/yum.repos.d/amzn2-extras.repo")

##echo "ALREADY_HAS_XTRAS_PHP72: $ALREADY_HAS_XTRAS_PHP72"

if [[ $ALREADY_HAS_XTRAS_PHP72 != "" ]]; then
  echo "Already enabled:        amzn2extra-php7.2"
elif [[ -e "/usr/local/pbase-data/pbase-preconfig-next/etc-yum-repos-d/amzn2/amzn2extra-php72.repo" ]]; then
  if [[ -e "/etc/yum.repos.d/amzn2extra-php72.repo" ]]; then
    echo "Already exists:          amzn2extra-php72.repo"
  else
    echo "AMZN2 PHP 7.2 repo:      amzn2extra-php72.repo"
    /bin/cp -f /usr/local/pbase-data/pbase-preconfig-next/etc-yum-repos-d/amzn2/amzn2extra-php72.repo /etc/yum.repos.d/
  fi
else
  echo "Not found:               amzn2extra-php72.repo"
  echo "Run this instead:        amazon-linux-extras install php7.2"
fi

#echo "complete"
%files
