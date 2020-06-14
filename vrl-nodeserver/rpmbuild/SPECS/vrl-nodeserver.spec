Name: vrl-nodeserver
Version: 1.0
Release: 0
Summary: VRL Asset Info editor Node JS service
Group: System Environment/Base
License: Apache-2.0
URL: https://pbase-foundation.com
Source0: vrl-nodeserver-1.0.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot 

Provides: vrl-nodeserver
Requires: nodejs

%description
VRL Asset Info editor Node JS service

%prep
%setup -q

%install
mkdir -p "$RPM_BUILD_ROOT"
cp -R * "$RPM_BUILD_ROOT"

%clean
rm -rf "$RPM_BUILD_ROOT"

%pre
echo "rpm preinstall $1"

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

echo "AssetInfo service"
mkdir -p /usr/local/nodeserver/
tar zxf /usr/local/pbase-data/vrl-nodeserver/assetinfo-server.tar.gz -C /usr/local/nodeserver/

echo "Service Node JS code:  /usr/local/nodeserver/assetinfo-server"
echo "Enabling service:      /etc/systemd/service/nodeserver.service"

systemctl daemon-reload
systemctl enable nodeserver.service
systemctl start nodeserver.service

systemctl status -l nodeserver.service
echo ""

echo "Configured Proxy:        /etc/httpd/conf.d/assetinfo-proxy.conf"
echo "Restarting Apache"

systemctl restart httpd
echo ""


%files
%defattr(-,root,root,-)
/etc/httpd/conf.d/assetinfo-proxy.conf
/etc/systemd/system/nodeserver.service
/usr/local/pbase-data/vrl-nodeserver/assetinfo-server.tar.gz
