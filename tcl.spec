%define rel	6
%define pre	b1

%if %pre
%define release		%mkrel 0.%{pre}.%{rel}
%define distname	%{name}%{version}%{pre}-src.tar.gz
%define dirname		%{name}%{version}%{pre}
%else
%define release		%mkrel %{rel}
%define distname	%{name}%{version}-src.tar.gz
%define dirname		%{name}%{version}
%endif

%define major		8.6
%define libname		%mklibname %{name} %{major}
%define develname	%mklibname %{name} -d

Summary:	An embeddable scripting language
Name:		tcl
Version:	8.6
Release:	%{release}
Group:		System/Libraries
License:	BSD
URL:		http://tcl.tk
Source0:	http://downloads.sourceforge.net/%{name}/%{distname}
Source1:	tcl.macros
Patch0:		tcl-8.5a6-soname.patch
Patch1:		tcl-8.6-dlopen.patch
# From Fedora, replaces old p6 by Stew, rediffed for 8.6 - AdamW 2008/10
Patch2:		tcl-8.6-autopath.patch
Patch3:		tcl-8.6b1-fix_includes.patch
Patch4:		tcl-8.5.0-expect-5.43.0.patch
Patch5:		tcl-8.6b1-tdbc_location.patch
# Originally from Gentoo, fix buffer overflow with GCC 4.5 -D_FORTIFY_SOURCE=2 - wally 2010/12
Patch6:		tcl8.6b1-fortify.patch
Buildroot:	%{_tmppath}/%{name}-%{version}

%description
Tcl is a simple scripting language designed to be embedded into
other applications.  Tcl is designed to be used with Tk, a widget
set, which is provided in the tk package.  This package also includes
tclsh, a simple example of a Tcl application.

If you're installing the tcl package and you want to use Tcl for
development, you should also install the tk and tclx packages.

%package -n	%{libname}
Summary:	Shared libraries for %{name}
Group:		System/Libraries

%description -n %{libname}
Tcl is a simple scripting language designed to be embedded into
other applications.  Tcl is designed to be used with Tk, a widget
set, which is provided in the tk package.  This package also includes
tclsh, a simple example of a Tcl application.

If you're installing the tcl package and you want to use Tcl for
development, you should also install the tk and tclx packages.

%package -n	%{develname}
Summary:	Development files for %{name}
Group:		Development/Other
Requires:	%{name} = %{version}-%{release}
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%mklibname tcl 8.4 -d
Obsoletes:	%mklibname tcl 8.5 -d

%description -n	%{develname}
This package contains development files for %{name}.

%prep
%setup -q -n %{dirname}
%patch0 -p1 -b .soname
%patch1 -p1 -b .dlopen
%patch2 -p1 -b .autopath
%patch3 -p1
%patch4 -p1 -b .expect
%patch5 -p1 -b .tdbc_location
%patch6 -p1 -b .fortify

%build
pushd pkgs/tdbc1.0b1
autoconf
popd

pushd unix
    autoconf
    %configure2_5x \
	--enable-threads \
	--enable-gcc \
	--enable-64bit \
	--disable-rpath \
	--includedir=%{_includedir}/tcl%{version}
    %make TCL_LIBRARY=%{_datadir}/%{name}%{major}

    cp libtcl%{major}.so libtcl%{major}.so.0
#    make test
popd

%install
rm -rf %{buildroot}

%makeinstall -C unix TCL_LIBRARY=%{buildroot}%{_datadir}/%{name}%{major}

# create the arch-dependent dir
mkdir -p %{buildroot}%{_libdir}/%{name}%{major}

# fix libname
mv %{buildroot}%{_libdir}/libtcl%{major}.so %{buildroot}%{_libdir}/libtcl%{major}.so.0
ln -snf libtcl%{major}.so.0 %{buildroot}%{_libdir}/libtcl%{major}.so

# install all headers
install -d %{buildroot}%{_includedir}/tcl%{version}/compat
install -d %{buildroot}%{_includedir}/tcl%{version}/generic
install -d %{buildroot}%{_includedir}/tcl%{version}/unix
install -m0644 compat/*.h %{buildroot}%{_includedir}/tcl%{version}/compat/
install -m0644 generic/*.h %{buildroot}%{_includedir}/tcl%{version}/generic/
install -m0644 unix/*.h %{buildroot}%{_includedir}/tcl%{version}/unix/

pushd %{buildroot}%{_bindir}
    ln -fs tclsh* tclsh
popd

pushd %{buildroot}%{_libdir}
cat > lib%{name}.so << EOF
/* GNU ld script
   We want -l%{name} to include the actual system library,
   which is lib%{name}%{major}.so.0  */
INPUT ( -l%{name}%{major} )
EOF
popd

# fix config script
perl -pi -e "s|-L`pwd`/unix\b|-L%{_libdir}|g" %{buildroot}%{_libdir}/tclConfig.sh
perl -pi -e "s|`pwd`/unix/lib|%{_libdir}/lib|g" %{buildroot}%{_libdir}/tclConfig.sh
perl -pi -e "s|`pwd`|%{_includedir}/tcl%{version}|g" %{buildroot}%{_libdir}/tclConfig.sh

# and let it be found (we don't look in /usr/lib any more)
ln -s %{_libdir}/%{name}Config.sh %{buildroot}/%{_libdir}/%{name}%{major}/%{name}Config.sh

# Arrangements for lib64 platforms
echo "# placeholder" >> %{develname}.files
if [[ "%{_lib}" != "lib" ]]; then
    mkdir -p %{buildroot}%{_prefix}/lib
    ln -s %{_libdir}/tclConfig.sh %{buildroot}%{_prefix}/lib/tclConfig.sh
    echo "%{_prefix}/lib/tclConfig.sh" >> %{develname}.files
fi

# (fc) make sure .so files are writable by root
chmod 755 %{buildroot}%{_libdir}/*.so*

# set up the macros
mkdir -p %{buildroot}%{_sys_macros_dir}
install -m 0644 %{SOURCE1} %{buildroot}%{_sys_macros_dir}

# move this tdbc crap around
mv %{buildroot}%{_libdir}/%{name}%{major}/tdbc*/libtdbc*.a %{buildroot}%{_libdir}

%if %mdkversion < 200900
%post -p /sbin/ldconfig -n %{libname}
%endif

%if %mdkversion < 200900
%postun -p /sbin/ldconfig -n %{libname}
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_bindir}/*
%{_datadir}/%{name}%{major}
%{_mandir}/man1/*
%{_mandir}/man3/*
%{_mandir}/mann/*
%{_datadir}/tcl8
%{_libdir}/%{name}%{major}
%exclude %{_libdir}/%{name}%{major}/tdbc*/tdbcConfig.sh

%files -n %{libname}
%defattr(-,root,root)
%attr(0755,root,root) %{_libdir}/lib*.so.*

%files -n %{develname} -f %{develname}.files
%defattr(-,root,root)
%dir %{_includedir}/tcl%{version}
%dir %{_includedir}/tcl%{version}/compat
%dir %{_includedir}/tcl%{version}/generic
%dir %{_includedir}/tcl%{version}/unix
%attr(0644,root,root) %{_includedir}/tcl%{version}/compat/*.h
%attr(0644,root,root) %{_includedir}/tcl%{version}/generic/*.h
%attr(0644,root,root) %{_includedir}/tcl%{version}/unix/*.h
%attr(0644,root,root) %{_includedir}/*.h
%attr(0755,root,root) %{_libdir}/*.so
%attr(0644,root,root) %{_libdir}/*.a
%attr(0755,root,root) %{_libdir}/tclConfig.sh
%attr(0755,root,root) %{_libdir}/%{name}%{major}/tdbc*/tdbcConfig.sh
%attr(0644,root,root) %{_sys_macros_dir}/tcl.macros

