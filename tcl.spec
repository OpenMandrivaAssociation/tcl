%define major %(echo %{version} |cut -d. -f1-2)
# temporary workaround for incorrect sonaming previously..
%define libname	%{mklibname %{name} %{major}}_not0
%define devname	%mklibname %{name} -d
%define _disable_lto 1

Summary:	Tool Command Language, pronounced tickle
Name:		tcl
Version:	8.6.8
Release:	4
Group:		System/Libraries
License:	BSD
URL:		http://tcl.tk
Source0:	http://downloads.sourceforge.net/%{name}/%{name}%{version}%{?pre}-src.tar.gz
Source1:	tcl.macros
Source2:	tcl.rpmlintrc
BuildRequires:	pkgconfig(zlib)
BuildRequires:	timezone
Patch0:		tcl-8.6.1-conf.patch
# From Fedora, replaces old p6 by Stew, rediffed for 8.6 - AdamW 2008/10
Patch2:		tcl-8.6.0-autopath.patch
Patch3:		tcl-8.6.1-fix_includes.patch
Patch4:		tcl-8.6.0-expect-5.43.0.patch
# dead?
#Patch5:		tcl-8.6b1-tdbc_location.patch
Patch6:		tcl-8.6.0-add-missing-linkage-against-libdl.patch
Patch7:		tcl-8.4.19-strtod.patch
Provides:	/usr/bin/tclsh
Provides:	tcl(abi) = %{major}
Recommends:	tcl-doc >= %{EVRD}

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

%package -n	%{devname}
Summary:	Development files for %{name}
Group:		Development/Other
Requires:	%{name} = %{version}-%{release}
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%mklibname tcl 8.4 -d
Obsoletes:	%mklibname tcl 8.5 -d

%description -n	%{devname}
This package contains development files for %{name}.

%package doc
Summary:	Documentation files for %{name}
Group:		Development/Other
Requires:	%{name} = %{EVRD}

%description doc
Documentation files for %{name}.

%prep
%setup -q -n %{name}%{version}%{?pre}
rm -r compat/zlib
rm -rf pkgs/sqlite3
chmod -x generic/tclStrToD.c

%patch0 -p1 -b .conf~
%patch2 -p1 -b .autopath~
%patch3 -p1 -b .includes~
%patch4 -p1 -b .expect~
#patch5 -p1 -b .tdbc_location~
%patch6 -p1
%patch7 -p1 -b .strod

%build
export CC=gcc
export CXX=g++
cd unix
autoconf
%configure \
    --enable-threads \
    --enable-64bit \
    --enable-symbols \
    --enable-shared \
    --disable-rpath \
    --without-tzdata \
    --includedir=%{_includedir}/tcl%{version}

%make_build CFLAGS="%{optflags}" TCL_LIBRARY=%{_datadir}/%{name}%{major}

cd -

%check
make -C unix test

%install
%make_install -C unix TCL_LIBRARY=%{buildroot}%{_datadir}/%{name}%{major}

ln -s tclsh%{major} %{buildroot}%{_bindir}/tclsh

# for linking with -lib%%{name}
ln -s lib%{name}%{major}.so %{buildroot}%{_libdir}/lib%{name}.so

mkdir -p %{buildroot}/%{_libdir}/%{name}%{major}

# postgresql and maybe other packages too need tclConfig.sh
# paths don't look at /usr/lib for efficiency, so we symlink into tcl8.6 for now
ln -s %{_libdir}/%{name}Config.sh %{buildroot}/%{_libdir}/%{name}%{major}/%{name}Config.sh

mkdir -p %{buildroot}/%{_includedir}/%{name}-private/{generic,unix}
find generic unix -name "*.h" -exec cp -p '{}' %{buildroot}/%{_includedir}/%{name}-private/'{}' ';'
( cd %{buildroot}/%{_includedir}
	for i in *.h ; do
		[ -f %{buildroot}/%{_includedir}/%{name}-private/generic/$i ] && ln -sf ../../$i %{buildroot}/%{_includedir}/%{name}-private/generic ||: ;
	done
)

# remove buildroot traces
sed -i -e "s|$PWD/unix|%{_libdir}|; s|$PWD|%{_includedir}/%{name}-private|" %{buildroot}/%{_libdir}/%{name}Config.sh
rm -rf %{buildroot}/%{_datadir}/%{name}%{major}/ldAix

install -m 0644 -D %{SOURCE1} %{buildroot}%{_sysconfdir}/rpm/macros.d/%{name}.macros

%files
%{_bindir}/*
%{_mandir}/man1/*
%{_libdir}/%{name}%{major}
%exclude %{_libdir}/%{name}%{major}/*Config.sh
%{_libdir}/itcl4.*
%{_libdir}/sqlite3.*
%dir %{_libdir}/tcl8
%dir %{_libdir}/tcl8/%{major}
%{_libdir}/tcl8/%{major}/tdbc
%{_libdir}/tdbc1.*
%{_libdir}/tdbcmysql1.*
%{_libdir}/tdbcodbc1.*
%{_libdir}/tdbcpostgres1.*
%{_libdir}/thread2.*

%files -n %{libname}
%{_libdir}/libtcl%{major}.so

%files -n %{devname}
%dir %{_includedir}/tcl-private
%{_includedir}/*
%{_includedir}/tcl-private/*
%{_libdir}/libtcl.so
%{_libdir}/lib*stub*.a
%{_libdir}/tcl*Config.sh
%{_libdir}/%{name}%{major}/*Config.sh
%{_sysconfdir}/rpm/macros.d/%{name}.macros
%{_libdir}/pkgconfig/*.pc

%files doc
%{_mandir}/man3/*
%{_mandir}/mann/*
