%define rel	11
%define pre	b1

%if %pre
%define release		%mkrel 0.%{pre}.%{rel}
%define distname	%{name}%{version}%{pre}-src.tar.gz
%define setname		%{name}%{version}%{pre}
%else
%define release		%mkrel %{rel}
%define distname	%{name}%{version}-src.tar.gz
%define setname		%{name}%{version}
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
BuildRequires:	zlib-devel
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
Provides:   /usr/bin/tclsh
Obsoletes:  %{name} < %{version}

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
%setup -q -n %{setname}
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



%changelog
* Tue Apr 26 2011 Paulo Andrade <pcpa@mandriva.com.br> 8.6-0.b1.8mdv2011.0
+ Revision: 659432
- Add zlib-devel to build requires

* Thu Mar 24 2011 Paulo Andrade <pcpa@mandriva.com.br> 8.6-0.b1.7
+ Revision: 648380
- Rebuild

* Mon Jan 24 2011 Paulo Andrade <pcpa@mandriva.com.br> 8.6-0.b1.6
+ Revision: 632487
- Rebuild for newer libxml2

* Mon Dec 06 2010 Jani Välimaa <wally@mandriva.org> 8.6-0.b1.5mdv2011.0
+ Revision: 612610
- add patch to fix buffer overflow with GCC 4.5 -D_FORTIFY_SOURCE=2
  (patch originally from Gentoo)

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 8.6-0.b1.4mdv2011.0
+ Revision: 607983
- rebuild

* Sun Jan 03 2010 Funda Wang <fwang@mandriva.org> 8.6-0.b1.3mdv2010.1
+ Revision: 486057
- Build with thread support

* Thu Sep 03 2009 Christophe Fergeau <cfergeau@mandriva.com> 8.6-0.b1.2mdv2010.0
+ Revision: 427285
- rebuild

* Wed Dec 24 2008 Adam Williamson <awilliamson@mandriva.org> 8.6-0.b1.1mdv2009.1
+ Revision: 318164
- a few adjustments to accomodate the inclusion of tdbc
- add tdbc_location.patch to install tdbc to the right place
- rediff fix_includes.patch
- new release 8.6b1

* Fri Dec 05 2008 Adam Williamson <awilliamson@mandriva.org> 8.6-0.a3.1mdv2009.1
+ Revision: 310122
- missing prefix/lib on x86-64
- new directory conventions: /usr/share/tcl8.6 (noarch) and /usr/lib/tcl8.6
- disable threaded build (#42596)
- drop libtcl-devel provide (everything should use tcl-devel now)
- drop manual dep on lib (one is auto-generated anyway)
- rediff autopath.patch and don't include /usr/lib in it any more
- add build macros (see policy page, coming soon!, for details)
- add pre-release build conditionals
- new release 8.6a3

* Wed Oct 15 2008 Frederik Himpe <fhimpe@mandriva.org> 8.5.5-1mdv2009.1
+ Revision: 294061
- update to new version 8.5.5

* Fri Aug 15 2008 Adam Williamson <awilliamson@mandriva.org> 8.5.4-1mdv2009.0
+ Revision: 272386
- new release 8.5.4

* Mon Jul 07 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 8.5.3-1mdv2009.0
+ Revision: 232454
- update to new version 8.5.3

* Tue Jun 24 2008 Adam Williamson <awilliamson@mandriva.org> 8.5.2-1mdv2009.0
+ Revision: 228719
- new release 8.5.2

* Wed Jun 18 2008 Thierry Vignaud <tv@mandriva.org> 8.5.1-3mdv2009.0
+ Revision: 225643
- rebuild

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Tue Mar 18 2008 Adam Williamson <awilliamson@mandriva.org> 8.5.1-2mdv2008.1
+ Revision: 188739
- update autopath.patch from Fedora and also adjust it to include libdir, as we install some tcl modules just in libdir (this was breaking at least tcl-snack, probably others)

* Tue Feb 05 2008 Frederik Himpe <fhimpe@mandriva.org> 8.5.1-1mdv2008.1
+ Revision: 162815
- New upstream bug fix release

* Sat Jan 12 2008 Adam Williamson <awilliamson@mandriva.org> 8.5.0-1mdv2008.1
+ Revision: 149224
- explicitly state 'tcl' in the -devel obsoletes, don't use %%{name}
- replace rpath.patch with a configure option
- rediff expect-5.43.0.patch
- rediff dlopen.patch as per FIXME in spec, replace auto_path.patch with one from Fedora
- rearrange spec to follow MDV norms
- new release 8.5.0 final

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Fri Sep 07 2007 Anssi Hannula <anssi@mandriva.org> 8.5a6-4mdv2008.0
+ Revision: 81976
- own dirs in /usr/lib/tcl8
- rediff and reapply rpath and soname patches

* Wed Jun 20 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 8.5a6-3mdv2008.0
+ Revision: 41807
- update url
- handle nicely some stubborn files
- new devel library policy

* Tue Jun 12 2007 Christiaan Welvaart <spturtle@mandriva.org> 8.5a6-2mdv2008.0
+ Revision: 38092
- patch8: export two internal functions for expect

* Thu May 31 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 8.5a6-1mdv2008.0
+ Revision: 33182
- new version
- own missing file

* Mon May 21 2007 Jérôme Soyer <saispo@mandriva.org> 8.5a5-6mdv2008.0
+ Revision: 29223
- Bump Release
- Bump Release
- Add Patch for fixing bug #30895

* Mon May 14 2007 Michael Scherer <misc@mandriva.org> 8.5a5-4mdv2008.0
+ Revision: 26605
- fix tcl-devel not installable

* Tue May 08 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 8.5a5-3mdv2008.0
+ Revision: 24998
- correct requires
- obsolete tcl8.4

  + Anssi Hannula <anssi@mandriva.org>
    - add conflict for previous version of -devel

* Thu Apr 19 2007 Jérôme Soyer <saispo@mandriva.org> 8.5a5-1mdv2008.0
+ Revision: 15001
- New release 8.5


* Mon Dec 18 2006 Nicolas Lécureuil <neoclust@mandriva.org> 8.4.14-1mdv2007.0
+ Revision: 98570
- Sync sources
- New version 8.4.14
- Import tcl

* Sat Apr 22 2006 Oden Eriksson <oeriksson@mandriva.com> 8.4.13-1mdk
- 8.4.13
- drop upstream patches; P5

* Tue Feb 14 2006 Stew Benedict <sbenedict@mandriva.com> 8.4.12-2mdk
- P6: add %%_libdir to $::auto_path on 64bit platforms
  (so addons like tcl-snack will work)

* Tue Feb 14 2006 Oden Eriksson <oeriksson@mandriva.com> 8.4.12-1mdk
- 8.4.12
- added P5 from cvs to fix build with bash3.1

* Sun Jan 01 2006 Oden Eriksson <oeriksson@mandriva.com> 8.4.11-6mdk
- fix the tclConfig.sh file

* Sat Dec 31 2005 Oden Eriksson <oeriksson@mandriva.com> 8.4.11-5mdk
- fix the tclConfig.sh file

* Sat Dec 31 2005 Oden Eriksson <oeriksson@mandriva.com> 8.4.11-4mdk
- fix the libtcl.so file

* Sat Dec 31 2005 Oden Eriksson <oeriksson@mandriva.com> 8.4.11-3mdk
- fix soname (P1) after looking at debian
- ship missing headers
- run the test suite
- misc lib64 and spec file fixes

* Thu Dec 29 2005 Guillaume Rousse <guillomovitch@mandriva.org> 8.4.11-2mdk
- first release as a standalone package
- devel files in a devel package
- nuke rpath for real

