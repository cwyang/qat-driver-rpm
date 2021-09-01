Summary: cwyang's Intel QAT driver RPM package
Name: qat
Version: 1.7.l.4.11.0
Release: 00001
Group: System Environment/Kernel
ExclusiveOS: linux
Vendor: Intel Corporation
License: GPL-2.0
Source0: %{source}
Source1: qat_contig_mem.tar.gz
URL: https://01.org/sites/default/files/downloads/%{source}
Patch0: uname_r.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-root
Provides: %{name}
Requires: pciutils
%{!?orgname: %global orgname cwyang}
%{!?kver: %global kver `uname -r`}
%global source %{name}%{version}-%{release}.tar.gz
%global basedir /opt/%{orgname}
%global qatbasedir %{basedir}/%{name}
%global qatsrcdir %{qatbasedir}/%{name}%{version}
%global qatbuilddir %{qatsrcdir}/build
%define debug_package %{nil}
%define _rpmfilename %{name}-%{version}-%{release}.%{kver}.rpm

# Check for existence of %kernel_module_package_buildreqs ...
%if 0%{?!kernel_module_package_buildreqs:1}
# ... and provide a suitable definition if it is not defined
%define kernel_module_package_buildreqs kernel-devel
%endif

BuildRequires: %kernel_module_package_buildreqs

%description
Intel(R) QuickAssist Technology Driver for Linux version %{version}-%{release}.

Following data can be specified by `rpmbuild --define "key value"`:
- orgname [RPM build files are located to /opt/{orgname}]
- kver    [Kernel version to build driver. Use running kernel if ommitted]
- privkey [Kernel module signing private key file. No sign if ommited]
- pubkey  [Kernel module signing public key file]

%prep
%setup -c -b 1
%patch0 -p1

%build
KSP=(/lib/modules/%{kver}/source \
        /lib/modules/%{kver}/build \
        /usr/src/linux-%{kver} \
        /usr/src/linux-$(echo %{kver} | sed 's/-.*//') \
        /usr/src/kernel-headers-%{kver} \
        /usr/src/kernel-source-%{kver} \
        /usr/src/linux-$(echo %{kver} | sed 's/\([0-9]*\.[0-9]*\)\..*/\1/') \
        /usr/src/linux \
        /usr/src/kernels/%{kver} \
        /usr/src/kernels)
KSRCS=( $(for i in ${KSP[@]}; do if [ -e $i/include/linux ]; then echo $i; fi;  done) )

export KERNEL_SOURCE_ROOT=${KSRCS[0]}
export ICP_AUTO_DEVICE_RESET_ON_HB=1
echo "Building qat driver on kernel %{kver}.."
%configure
make %{?_smp_mflags} all #samples
export PATH_AUTOCNF=include/generated # for centos
echo "Building qat_contig_mem driver on kernel %{kver}.."
(cd qat_contig_mem; make %{?_smp_mflags} all)
%install
rm -rf %{buildroot}
sed -i 's/NumProcesses = 1/NumProcesses = 2/' build/*.conf build/*.conf.vm
make INSTALL_MOD_PATH=%{buildroot} %{?_smp_mflags} qat-driver-install
make INSTALL_MOD_PATH=%{buildroot} INSTALL_MOD_DIR=updates -C /lib/modules/%{kver}/build M=`pwd`/qat_contig_mem mod_sign_cmd=":" modules_install

mkdir -p %{buildroot}%{qatbuilddir}
cp %{_sourcedir}/%{source} %{buildroot}%{qatbasedir}
cp build/* %{buildroot}%{qatbuilddir}
cp Makefile %{buildroot}%{qatsrcdir}

# Remove modules files that we do not want to include
find %{buildroot}/lib/modules/ -name 'modules.*' -exec rm -f {} \;
(cd %{buildroot}; find lib -name "*.ko" \
	-fprintf %{_builddir}/%{name}-%{version}/file.list "/%p\n")

# Strip the modules(s).
DS="%{dist}" && [ -z "${DS##*dev*}" ] || \
        find %{buildroot} -type f -name \*.ko -exec %{__strip} --strip-debug \{\} \;

# sign all modules if privkey is provided
%if 0%{?privkey:1}
for module in $(find %{buildroot} -type f -name \*.ko); do
    %{__perl} /usr/src/kernels/%{kver}/scripts/sign-file sha256 %{privkey} %{pubkey} $module;
done
%endif

%clean
rm -rf %{buildroot}

%files -f file.list

%defattr(-,root,qat)
%doc file.list
%dir %{qatbasedir}/
%{qatbasedir}/%{source}
%{qatsrcdir}/Makefile
%{qatbuilddir}/*

%pre
if [ ! -f /etc/qat-force ]; then
	if [ -f /etc/redhat-release ]; then
		major=`cat /etc/redhat-release |  awk -F'[^0-9.]*' '$0=$2' | awk -F "." '{ print $1 }'`
		minor=`cat /etc/redhat-release |  awk -F'[^0-9.]*' '$0=$2' | awk -F "." '{ print $2 }'`
		if (( major == 7 )); then
			if (( minor < 2 )); then
				echo Minor number too small
				exit 1
			fi
			if (( minor > 9	)); then
				echo Minor number too large
				exit 1
			fi
		else
			echo Unknown or unsupported Linux version
			exit 1
		fi
	else
		echo Unknown or unsupported Linux disto
		exit 1
	fi
else
	echo Experimental configuration.
fi
groupadd -f qat

%post
if [ -f /etc/init.d/qat_service ]; then
	/etc/init.d/qat_service shutdown
fi

export ICP_ROOT=%{qatsrcdir}
export ICP_BUILD_OUTPUT=%{qatbuilddir}
export ICP_SRIOV_AM=0
if lspci -v |grep SR-IOV >& /dev/null; then
    ICP_SRIOV_AM=1
fi

tar xfz %{qatbasedir}/%{source} -C %{qatsrcdir}
cd %{qatsrcdir}
echo "%{name}-%{version} install started at $(date), kver=%{kver}, pwd=$(pwd), SR-IOV=${ICP_SRIOV_AM}" | tee -a %{qatbasedir}/install.txt

touch %{qatsrcdir}/config.status
make ADF_CTL_DIR=%{qatbuilddir} adf-ctl-install 2>&1 | tee -a %{qatbasedir}/install.txt
make KVER=%{kver} ICP_BUILD_OUTPUT=%{qatbuilddir} qat-service-install 2>&1 | tee -a %{qatbasedir}/install.txt
echo "qat_contig_mem" > /etc/modules-load.d/qat_contig_mem.conf | tee -a %{qatbasedir}/install.txt
modprobe qat_contig_mem

%postun
if [ $1 == 0 ]; then
    /etc/init.d/qat_service shutdown
    %{qatsrcdir}/make KVER=%{kver} qat-service-uninstall
fi

%changelog
* Wed Sep 1 2021 Chul-Woong Yang <cwyang@gmail.com>
- setting NumProcesses of qat device configuration file to 2
- create /etc/modules-load.d/qat_contig_mem.conf
* Fri Apr 2 2021 Chul-Woong Yang <cwyang@gmail.com>
- add qat_contig_mem.ko and modprobe it
* Thu Mar 18 2021 Chul-Woong Yang <cwyang@gmail.com>
- qat-service-[un]install uses %kver
* Tue Oct 6 2020 Chul-Woong Yang <cwyang@gmail.com>
- fix post to detect SR-IOV on target machine
* Sat Sep 26 2020 Chul-Woong Yang <cwyang@gmail.com>
- Initial work
