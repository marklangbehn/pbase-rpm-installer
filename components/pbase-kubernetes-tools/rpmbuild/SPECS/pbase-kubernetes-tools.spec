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
Requires: pbase-kvm, wget, curl

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

echo "PBase Kubernetes Tools Install"
echo ""

## download minikube and place it /usr/local/bin
cd /tmp
wget https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
chmod +x minikube-linux-amd64
mv minikube-linux-amd64 /usr/local/bin/minikube

## download kubectl command line tool and place it /usr/local/bin
cd /tmp
curl -s -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl
chmod +x kubectl
mv kubectl  /usr/local/bin/

## show kubectl info
## /usr/local/bin/kubectl version --client -o json


echo "Next step:               Install a KVM 'driver' such as:"
echo "                         docker, podman, virtualbox, vmware"
echo ""
echo "Next step:               Add you desktop username to KVM 'libvirt' group:"
echo "  usermod -a -G libvirt mydesktopusername"
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
