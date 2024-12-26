%global build_type_safety_c 0

%define prerel beta1
%define version_real 0.36.4_%{prerel}


Name:       gdesklets
Version:    0.36.4%{?prerel:~%{prerel}}
Release:    1%{?dist}
Summary:    Architecture for desktop applets
License:    GPLv2+
URL:        https://github.com/sergiomb2/gdesklets
Source0:    https://github.com/sergiomb2/gdesklets/archive/v%{version_real}/%{name}-%{version}.tar.gz

BuildRequires:  python2-devel > 2.0.0
BuildRequires:  gtk2-devel > 2.4.0
BuildRequires:  pygtk2-devel > 2.4.0
BuildRequires:  pygobject2-devel
BuildRequires:  librsvg2-devel
BuildRequires:  libgtop2-devel >= 2.8.0
BuildRequires:  libtool
BuildRequires:  gettext-devel
BuildRequires:  intltool
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils
#Requires: python-icalendar

Requires:   pygtk2

%description
'gDesklets' provides an advanced architecture for desktop applets -
tiny displays that sit on your desktop such as status meters, icon
bars, weather sensors, news tickers.


%prep
%setup -q -n %{name}-%{version_real}

%build
autoreconf -fiv
%configure \
 --disable-static \
 --enable-debug \
 --disable-update-check

%make_build

%install
make install DESTDIR=%{buildroot}
%find_lang %{name}
desktop-file-install \
    --delete-original \
    --dir=%{buildroot}%{_datadir}/applications \
        %{buildroot}%{_datadir}/applications/%{name}.desktop

mkdir -p  %{buildroot}{%{_bindir},%{_datadir}/%{name}/data/,%{_datadir}/%{name}/Displays/,%{_datadir}/%{name}/Controls/}

# don't want libtool archives
find %{buildroot} -name \*.la -delete

install -D -m0644 contrib/bash/gdesklets %{buildroot}/%{_datadir}/bash-completion/completions/gdesklets
install -Dp gdesklets.appdata.xml %{buildroot}/%{_datadir}/appdata/%{name}.appdata.xml
appstream-util validate-relax --nonet %{buildroot}/%{_datadir}/appdata/*.appdata.xml

%files -f %{name}.lang
%doc AUTHORS ChangeLog NEWS README
%license COPYING
%{_bindir}/gdesklets
%{_datadir}/mime/packages/gdesklets.xml
%{_datadir}/icons/gnome/48x48/mimetypes/*.png
%{_datadir}/pixmaps/gdesklets.png
%{_sysconfdir}/xdg/autostart/gdesklets.desktop
%{_datadir}/applications/*.desktop
%{_datadir}/gdesklets/
%{_libdir}/gdesklets/
%{_mandir}/man1/*
%{_datadir}/appdata/gdesklets.appdata.xml
%dir %{_datadir}/bash-completion
%dir %{_datadir}/bash-completion/completions
%{_datadir}/bash-completion/completions/gdesklets


%changelog
* Thu Dec 26 2024 Sérgio Basto <sergio@serjux.com> - 0.36.4~beta-1
- 0.36.4 Beta 1, try 3
  - try 2, Sun Oct 01 2023 0.36.4-0.1
  - try 1, Sun Oct 18 2015 0.36.4-0.1

* Tue Dec 24 2024 Sérgio Basto <sergio@serjux.com> - 0.36.3-39
- pygtk2 is needed provides the import gtk

* Mon Nov 09 2020 Sérgio Basto <sergio@serjux.com> - 0.36.3-37
- No gnome-python2

* Tue Sep 10 2019 Sérgio Basto <sergio@serjux.com> - 0.36.3-36
- Remove BR: libXau-devel libXdmcp-devel libgnome-devel gvfs-devel libcap-devel
  seems they aren't in use.

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.36.3-35
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.36.3-34
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Sat Oct 06 2018 Sérgio Basto <sergio@serjux.com> - 0.36.3-33
- Fix FTBFS

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.36.3-32
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.36.3-31
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Jan 12 2018 Leigh Scott <leigh123linux@googlemail.com> - 0.36.3-30
- Add missing requires pygtk2
- Fix shebangs so package requires python2

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.36.3-29
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.36.3-28
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Jun 13 2017 Kalev Lember <klember@redhat.com> - 0.36.3-27
- Rebuilt for libgtop2 soname bump

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.36.3-26
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.36.3-25
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Sep 23 2015 Sérgio Basto <sergio@serjux.com> - 0.36.3-24
- Minor simplification

* Thu Aug 06 2015 Sérgio Basto <sergio@serjux.com> - 0.36.3-23
- Use gconf optionally, Added patch from
  http://bazaar.launchpad.net/~ballogy/gdesklets/optional-use-gconf-appindicator/revision/188
  and drop Requires: gnome-python2-gconf
- Add gdesklets-checkrequiments.patch, don't check pyorbit and put bonobo python bindings as optional,
  also removes the old file gdesklets-migration-tool .

* Thu Jul 16 2015 Sérgio Basto <sergio@serjux.com> - 0.36.3-22
- Removed 182_181.diff

* Wed Jul 15 2015 Sérgio Basto <sergio@serjux.com> - 0.36.3-21
- Added 187_186.diff (#1243415) and 182_181.diff .
- Removed BuildRequires pyorbit (Retired on F23+), looks like gdesklets not need it.

* Sat Jul 04 2015 Sérgio Basto <sergio@serjux.com> - 0.36.3-20
- Enable debug for debuginfo package.
- Disable update check.
- Removed disable-schemas-install.

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.36.3-19
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Jun 09 2015 Sérgio Basto <sergio@serjux.com> - 0.36.3-18
- Added 8 patches from upstream.
- Removed vfs.patch (https://bugs.launchpad.net/gdesklets/+bug/890817 , I
  agree with comment #2.)
- Removed gdesklets-aarch64.patch and use autoreconf instead.
- Added patch to fix obsoleted m4s.
- Added desktop-database scriptlet.
- Fix License tag and License macro.
- Spec clean up.
- Fix mixed-use-of-spaces-and-tabs.
- Added AppData https://fedoraproject.org/wiki/Packaging:AppData

* Sat Sep 27 2014 Rex Dieter <rdieter@fedoraproject.org> 0.36.3-17
- update mimeinfo scriptlets

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.36.3-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.36.3-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu May 01 2014 Kalev Lember <kalevlember@gmail.com> - 0.36.3-14
- Rebuilt for libgtop2 soname bump

* Fri Aug 16 2013 * Mon Apr 16 2012 Luya Tshimblanaga <luya@fedoraproject.org> - 0.36.3-13
- Patch to support aarch64

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.36.3-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Mar 14 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 0.36.3-11
- Use the more careful and latest conditional to detect Fedora < 19. 

* Thu Mar 14 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 0.36.3-10
- Remove desktop vendor prefix for Fedora >= 19.
- Don't include .desktop.in and MIME .xml.in template files.
- Build with --disable-static and don't include libtool archives (#889607).

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.36.3-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.36.3-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Apr 16 2012 Luya Tshimblanaga <luya@fedoraproject.org> - 0.36.3-7
- Bump to address upgradepath autoqa failure

* Tue Mar 20 2012 Luya Tshimbalanga <luya@fedoraproject.org> - 0.36.3-6
- Adhered to Fedora guideline for desktop declaration
- Ported patch from OpenSuse spec version
- Patch addressing memory leak (rhbz #747420, launchpad #190894)

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.36.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Dec 06 2011 Adam Jackson <ajax@redhat.com> - 0.36.3-4
- Rebuild for new libpng

* Mon Dec 05 2011 Luya Tshimbalanga <luya@fedoraproject.org> - 0.36.3-3
- Patch for vfs declaration (rhbz#740610)
- Added gvfs-devel and python3-devel for BuildRequires

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.36.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Jan 27 2011 Luya Tshimbalanga <luya@fedoraproject.org> - 0.36.3-1
- New upstream version
- Fixes spec

* Wed Aug 11 2010 David Malcolm <dmalcolm@redhat.com> - 0.36.2-3
- recompiling .py files against Python 2.7 (rhbz#623304)

* Wed Mar 03 2010 Luya Tshimbalanga <luya@fedoraproject.org> 0.36.2-2
- Changed summary sentence (rhbz#588330)

* Wed Mar 03 2010 Luya Tshimbalanga <luya@fedoraproject.org> 0.36.2-1.1
- New upstream version
- Dropped patch related to python 2.6 compatibility

* Thu Oct 29 2009 Luya Tshimbalanga <luya@fedoraproject.org> 0.36.1-7
- Add patch to address compatibility with python 2.6

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.36.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.36.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Dec 01 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.36.1-4
- Rebuild for Python 2.6

* Thu Nov 20 2008 Luya Tshimbalanga <luya@fedoraproject.org> - 0.36.1-3
- Updated from upstream
- (#472263) Removed autogenerated-mime data for integrating check
  courtesy of Christian Krause (chkr@plauener.de) 

* Fri Oct 03 2008 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.36-2
- Cleaned up spec
- Minor fixes

* Fri Feb 22 2008 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.36-1
- Update from upstream
- Added libcap-devel for dependancy

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.36-0.4.beta
- Autorebuild for GCC 4.3

* Fri Nov 23 2007 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.36.0-3.beta
- Changed url adress
- Added patch for dialog

* Thu Nov 15 2007 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.36.0-1.beta
- New beta release
- Removed patch

* Tue Aug 21 2007 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.4-9
- Renamed GPL to GPL+ following the new Fedora tagging license schema

* Sun Jul 15 2007 Tyler Owen <tyler.l.owen@gmail.com> - 0.35.4-8
- Added directory for Displays
- Added directory for Controls

* Thu Jun 07 2007 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.4-7.1
- Dropped Applet name category
- Replaced Accesories name category by Applet
- Added patch to remove old Xorg 6.8 notification for transition.py
- Removed no-longer needed python-abi

* Tue May 15 2007 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.4-5
- Rebuild with Koji

* Thu Dec 14 2006 Jason L Tibbitts III <tibbs@math.uh.edu> - 0.35.4-4
- Rebuild for new Python

* Tue Nov 07 2006 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.4-3
- Added gnome-python2-devel for buildrequires (rawhide)

* Tue Nov 07 2006 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.4-2
- Removed gnome-python for buildrequires

* Tue Nov 07 2006 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.4-1
- Removed patch no longer needed
- Updated to 0.35.4

* Thu Aug 31 2006 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.3-14
- Add patch related to pyorbit due to upstream bug

* Wed Aug 30 2006 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.3-13.2
- pyorbit for FC-4 is 2.0.1 (-_-)

* Wed Aug 30 2006 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.3-13
- Fixed a silly typo
- Added intltool for BuildRequires

* Sun Aug 27 2006 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.3-10
- Removed unecessary comment

* Wed Apr 19 2006 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.3-8
- Remove conditional sign for pyorbit-devel

* Mon Apr 03 2006 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.3-5
- Ajusted pyorbit requirement for ppc64

* Thu Jan 19 2006 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.3-4
- Rebuild for Fedora Extras 5

* Mon Jan 16 2006 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.3-1
- Updated to 0.35.3
- Removed thumbmail
- Removed patch, no longer needed

* Thu Jan 5 2006 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.2-26.fc5
- Minor rebuilt

* Thu Jan 5 2006 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.2-25.fc5
- Rebuilt against libgtop2-devel
- Changed url of the provider

* Sun Dec 18 2005 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.2-24.fc5
- Added libXdmcp-devel on BuildRequires

* Sun Dec 18 2005 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.2-23.fc5
- Added libXau-devel on BuildRequires

* Wed Dec 14 2005 Luya Tshimbalanga
 <luya_tfz@thefinalzone.com> - 0.35.2-22
- Added desktop-file-utils for build requirement
- Clean up

* Tue Dec 6 2005 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.2-21
- Removed unnecessary comment  
- More clean up

* Tue Dec 6 2005 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.2-20
- Clean up 
- Fixed the right path for symbolic link

* Sat Dec 3 2005 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.2-19
- Added disable-schemas-install on configure
- Trying to symlink using nrpms method based on FC3 version

* Tue Nov 29 2005 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.2-18
- Added patch against NullObject.py (thanks jwb)

* Tue Nov 29 2005 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.2-17
- Reorganized names and fixed install

* Mon Nov 21 2005 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.2-12
- Removed pygtk2

* Mon Nov 21 2005 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.2-11
- Added distribution version
- Clarified the note about GConf instead of gconf

* Fri Nov 18 2005 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.2-10
- Added libgnomeui-devel to test some sensors

* Fri Nov 18 2005 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.2-9
- Cleaned up and removed unnecesary buildrequires

* Fri Nov 18 2005 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.2-8
- Fixed error on mime.cache

* Wed Nov 16 2005 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.2-5
- Added desktop-file-utils command for post and postun

* Wed Nov 16 2005 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.2-4
- Fixed mistakes (thanks Alex Lancaster (alexl@users.sourceforge.net))

* Sat Nov 12 2005 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.2-3
- Enhanced codes to be FedoraGuide compliant (thanks to Brian Pepple (bdpepple@ameritech.net))

* Sat Nov 12 2005 Luya Tshimbalanga <luya_tfz@thefinalzone.com> - 0.35.2-1
- Initial Fedora Extras package
