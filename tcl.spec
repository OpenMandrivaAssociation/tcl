%define major %(echo %{version} |cut -d. -f1-2)
%define oldlibname %{mklibname %{name} %{major}}_not0
%define libname %mklibname %{name}
%define devname %mklibname %{name} -d

%ifnarch %{riscv}
%global optflags %{optflags} -fPIC --rtlib=compiler-rt
%else
%global optflags %{optflags} -fPIC
%endif
%global ldflags %{ldflags} -Wl,-z,notext


%bcond_without	sdt
%bcond_with	sqlite

Summary:	Tool Command Language, pronounced tickle
Name:		tcl
Version:	8.6.13
Release:	1
Group:		System/Libraries
License:	BSD
URL:		https://tcl.tk
Source0:	https://downloads.sourceforge.net/%{name}/%{name}%{version}-src.tar.gz
#Source0:	https://downloads.sourceforge.net/%{name}/%{name}-core%{version}-src.tar.gz
Source1:	tcl.macros
Source2:	tcl.rpmlintrc
# From Fedora, replaces old p6 by Stew, rediffed for 8.6 - AdamW 2008/10
Patch0:		https://src.fedoraproject.org/rpms/tcl/raw/rawhide/f/tcl-8.6.12-autopath.patch
Patch1:		https://src.fedoraproject.org/rpms/tcl/raw/rawhide/f/tcl-8.6.12-conf.patch
Patch2:		https://src.fedoraproject.org/rpms/tcl/raw/rawhide/f/tcl-8.6.12-hidden.patch
Patch3:		https://src.fedoraproject.org/rpms/tcl/raw/rawhide/f/tcl-8.6.10-tcltests-path-fix.patch

BuildRequires:	pkgconfig(zlib)
BuildRequires:	timezone
%{?with_sdt:BuildRequires:	systemtap-devel}

Provides:	/usr/bin/tclsh
Provides:	tcl(abi) = %{major}

%description
Tcl is a simple scripting language designed to be embedded into
other applications.  Tcl is designed to be used with Tk, a widget
set, which is provided in the tk package.  This package also includes
tclsh, a simple example of a Tcl application.

If you're installing the tcl package and you want to use Tcl for
development, you should also install the tk and tclx packages.

%files
%{_bindir}/*
%{_mandir}/man1/*
%{_libdir}/%{name}%{major}
%{_datadir}/%{name}%{major}
%{_datadir}/%{name}8
%exclude %{_libdir}/%{name}%{major}/*Config.sh
%{_libdir}/tcl8/%{major}

#--------------------------------------------------------------------

%package -n %{libname}
Summary:	Shared libraries for %{name}
Group:		System/Libraries
# Intentionally unversioned, because oldlibname was plain wrong
Obsoletes:	%{oldlibname}

%description -n %{libname}
Tcl is a simple scripting language designed to be embedded into
other applications.  Tcl is designed to be used with Tk, a widget
set, which is provided in the tk package.  This package also includes
tclsh, a simple example of a Tcl application.

If you're installing the tcl package and you want to use Tcl for
development, you should also install the tk and tclx packages.

%files -n %{libname}
%{_libdir}/libtcl%{major}.so

#--------------------------------------------------------------------

%package -n %{devname}
Summary:	Development files for %{name}
Group:		Development/Other
Requires:	%{name} = %{version}-%{release}
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%mklibname tcl 8.4 -d
Obsoletes:	%mklibname tcl 8.5 -d

%description -n %{devname}
This package contains development files for %{name}.

%files -n %{devname}
%{_includedir}/*.h
%dir %{_includedir}/tcl-private
%{_includedir}/tcl-private/*
%{_libdir}/libtcl.so
%{_libdir}/lib*stub*.a
%{_libdir}/tcl*Config.sh
%{_libdir}/%{name}%{major}/*Config.sh
%{_sysconfdir}/rpm/macros.d/%{name}.macros
%{_libdir}/pkgconfig/*.pc

#--------------------------------------------------------------------

%package doc
Summary:	Documentation files for %{name}
Group:		Development/Other
Requires:	%{name} = %{EVRD}

%description doc
Documentation files for %{name}.

%files doc
%{_mandir}/man3/*
%{_mandir}/mann/*

#--------------------------------------------------------------------

%prep
%autosetup -p1 -n %{name}%{version}

rm -r compat/zlib
%if !%{with sqlite}
rm -rf pkgs/sqlite3.*
%endif
chmod -x generic/tclStrToD.c

%build
pushd unix
%config_update
autoreconf -fiv
%configure \
	--enable-threads \
%ifnarch %{ix86}
	--enable-64bit \
%endif
	--enable-symbols \
	--enable-shared \
	--disable-rpath \
	--%{?with_sdt:en}%{!?with_sdt:dis}able-dtrace \
	--without-tzdata

%make_build CFLAGS="%{optflags}" LDFLAGS="%{ldflags}" TCL_LIBRARY="%{_datadir}/%{name}%{major}"
popd

%check
make -C unix test ||:

%install
%make_install -C unix TCL_LIBRARY="%{_datadir}/%{name}%{major}"

ln -s tclsh%{major} %{buildroot}%{_bindir}/tclsh

# for linking with -lib%%{name}
ln -s lib%{name}%{major}.so %{buildroot}%{_libdir}/lib%{name}.so

mkdir -p %{buildroot}/%{_libdir}/%{name}%{major}

# postgresql and maybe other packages too need tclConfig.sh
# paths don't look at /usr/lib for efficiency, so we symlink into tcl8.6 for now
ln -s %{_libdir}/%{name}Config.sh %{buildroot}/%{_libdir}/%{name}%{major}/%{name}Config.sh

mkdir -p %{buildroot}%{_includedir}/%{name}-private/{generic,unix}
find generic unix -name "*.h" -exec cp -p '{}' %{buildroot}%{_includedir}/%{name}-private/'{}' ';'
( cd %{buildroot}/%{_includedir}
	for i in $(ls -1 *.h) ; do
		[ -f %{buildroot}%{_includedir}/%{name}-private/generic/$i ] && ln -sf ../../$i %{buildroot}%{_includedir}/%{name}-private/generic ||: ;
	done
)

# remove buildroot traces
sed -i -e "s|$(pwd)/unix|%{_libdir}|; s|$(pwd)|%{_includedir}/%{name}-private|" %{buildroot}/%{_libdir}/%{name}Config.sh
rm -rf %{buildroot}/%{_datadir}/%{name}%{major}/ldAix

install -m 0644 -D %{SOURCE1} %{buildroot}%{_sysconfdir}/rpm/macros.d/%{name}.macros

for i in itcl4.2.3 sqlite3.40.0 tdbc1.1.5 tdbcmysql1.1.5 tdbcodbc1.1.5 tdbcpostgres1.1.5 thread2.8.8; do
	[ -d %{buildroot}%{_libdir}/"$i" ] && mv -f %{buildroot}%{_libdir}/"$i" %{buildroot}%{_libdir}/%{name}%{major}/"$i"
done

