Name: pbase-kvm
Version: 1.0
Release: 0
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

echo "PBase KVM Hypervisor Install"
echo ""

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

echo "Next steps:              Add your desktop username to KVM 'libvirt' group:"
echo ""
echo "  usermod -a -G libvirt mydesktopusername"
echo ""

%files
