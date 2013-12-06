Name:   collector-fluentd
Version:        1.0
Release:        el6
Summary:        collector-fluentd is a large-scale system metric collecting tool for fluentd

Group:          Applications/Server
License:        Apache Licence 2.0
URL:            https://github.com/fangli/collector-fluentd
SOURCE0:        https://github.com/fangli/collector-fluentd/releases/download/1.0/collector-fluentd-1.0.tar.gz
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%description
A large-scale system metrics collecting daemon tool for fluentd

%prep
%setup -c

%pre
if [ "" == "`which python`" ]; then
  echo "Python >= 2.4 required, please install python via 'yum install python'"
  exit -1
fi

%install
install -d %{buildroot}%{_libdir}/
mv collector-fluentd %{buildroot}%{_libdir}/
install -d %{buildroot}%{_initddir}
cp %{buildroot}%{_libdir}/collector-fluentd/etc/init.d/collector-fluentd %{buildroot}%{_initddir}/
install -d %{buildroot}%{_sysconfdir}/
cp %{buildroot}%{_libdir}/collector-fluentd/etc/collector-fluentd.conf %{buildroot}%{_sysconfdir}/collector-fluentd.conf


%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{_libdir}/*
%{_initddir}/*
%config %{_sysconfdir}/collector-fluentd.conf

%post
ln -snf %{_libdir}/collector-fluentd/collector-fluentd %{_bindir}/collector-fluentd
mkdir /tmp/collector-fluentd/ -p
/sbin/chkconfig --add collector-fluentd

%preun
  if [ $1 = 0 ]; then
      # package is being erased, not upgraded
      /sbin/service collector-fluentd stop
      /sbin/chkconfig --del collector-fluentd
  fi

%postun
  if [ $1 = 0 ]; then
      echo "Uninstalling collector-fluentd"
      rm %{_bindir}/collector-fluentd
      # package is being erased
      # Any needed actions here on uninstalls
  else
      # Upgrade
      /sbin/service collector-fluentd restart
  fi


%changelog
* Fri Dec 06 2013  Felix <surivlee@gmail.com>
  - Initial release
