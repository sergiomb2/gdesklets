INSERT INTO `gd_conf` (`conf_name`, `conf_value`) VALUES('site_bottom', 'The official inofficial gDesklets Website');
INSERT INTO `gd_conf` (`conf_name`, `conf_value`) VALUES('site_menu', '<a href=""?"" target=""_self"">Home</a> |
<a href=""?mod=show"" target=""_self"">FAQ</a> |
<a href=""?mod=docs"" target=""_self"">Documents</a> |
<a href=""http://www.pycage.de/develbook"" target=""_new"">Developer''s Book</a> |
<a href=""?mod=search"" target=""_self"">Search</a> |
<a href=""?mod=submit"" target=""_self"">Submit</a>');
INSERT INTO `gd_docs` (`doc_id`, `doc_author`, `doc_email`, `doc_title`, `doc_text`, `doc_released`) VALUES('3', 'a monkey', 'thechimp@earthlink.net', 'gDesklets General User''s Guide', '<hr/>
gDesklets general user''s guide by a monkey (<a href=""mailto:thechimp@earthlink.net"">thechimp@earthlink.net</a>)
Version 0.1
<hr/>

<p>Table of Contents
</p>
<p>I - Getting Started
</p>
<p>  I.1 - Downloading gDesklets<br/>
  I.2 - Installation<br/>
  I.3 - Firing up gDesklets
</p>
<p>II - Desklets
</p>
<p>  II.1 - Downloading Desklets<br/>
  II.2 - Installing a Desklet''s Sensor<br/>
  II.3 - Running the Display File
</p>
<p>III - Troubleshooting
</p>
<p>  III.1 - Do You Have Outdated Dependencies?
  III.2 - Upgrading Dependencies<br/>
  III.3 - I''m Hopeless!
</p>
<hr/>
I - Getting Started
<hr/>

<hr/>
I.1 - Downloading gDesklets
<hr/>

<p>You can download the latest version of gDesklets'' source code here:
</p>
<p><a href=""http://www.pycage.de/software_gdesklets.html"">http://www.pycage.de/software_gdesklets.html</a>
</p>
<p>Unpack the compressed tar.bz2 file like this:
</p>
<p>tar -jxvf gDesklets-&lt;version&gt;.tar.bz2
</p>
<hr/>
I.2 - Installation
<hr/>

<p>Hold your horses, there. First read the README file included in the folder you just unpacked. This will tell you how to install compile and install gDesklets in the first half of step 3. I''m not going to recite the README file for you, so do what I say, read it.
</p>
<hr/>
I.3 - Firing up gDesklets
<hr/>

<p>Once you''ve installed gDesklets as the first half of step 3 in the README told you, get to the command line, cross your fingers, and type
</p>
<p>gdesklets start
</p>
<p>If you get a timeout error when connecting to the gDesklets daemon, this generally means that you do not have the proper dependencies of gDesklets installed. Browse through step 2 of the README file to make sure that you have all of gDesklets'' dependencies installed at the proper versions. One mistake I made was trying to run gDesklets 0.32 with python-gnome 2.0.0. Also, make sure that you have the dependencies of gDesklets itself installed, not only the requirements for compiling gDesklets, e.g. pygtk itself instead of your distro''s pygtk-devel package.
</p>
<p>Once there are no errors after typing `gdesklets start'', this means you''ve successfully fired up gDesklets. But don''t get worried if you don''t see a bunch of eye-candy popping up all over your desktop, installing desklets comes later.
</p>
<hr/>
II - Desklets
<hr/>

<hr/>
II.1 - Downloading Desklets
<hr/>

<p>There are tons of desklets available for free at
</p>
<p><a href=""http://gdesklets.gnomedesktop.org/"">http://gdesklets.gnomedesktop.org/</a>
</p>
<p>Unpack a desklet like this:
</p>
<p>tar -jxvf &lt;desklet&gt;.tar.bz2
</p>
<hr/>
II.2 - Installing a Desklet''s Sensor and Controls
<hr/>

<p>You should be able to skip this step, now that sensors are deprecated. But if you see a sensor or a Install_&lt;desklet&gt;_Sensor.bin file, you should go through this step. You should copy sensors to ~/.gdesklets/Sensors/ using the `cp'' command (cp --help), or else run the installer:
</p>
<p>cd &lt;desklet directory&gt;<br/>
./Install_&lt;desklet&gt;_Sensor.bin
</p>
<ul>
  <li>NOTE: You should not be root when doing this.

</li></ul>
<p>If all goes well, you will get a message saying ""The sensor has been installed successfully. gDesklets is now able to use it.""
</p>
<p>Install a desklet''s controls by using the cp command to copy them to ~/.gdesklets/Controls/
</p>
<hr/>
II.3 - Running the Display File
<hr/>

<p>The README will tell you how to open a display file via gDesklets in the very beginning of step 5.1.
</p>
<hr/>
III - Troubleshooting
<hr/>

<hr/>
III.1 - Do You Have Outdated Dependencies?
<hr/>

<ul>
  <li>Note: Only people whose distro has an RPM-based package management system should proceed. I don''t know anything about other distros like Debian, so I won''t speak for them.

</li></ul>
<p>If you think you may have an outdated dependency, check if you do like this:
</p>
<p>rpm -qi &lt;package name&gt;
</p>
<p>If this shows that you have an outdated dependency, you should proceed to III.2.
</p>
<hr/>
III.2 - Upgrading Dependencies
<hr/>

<p>Try to stick to using RPMs to upgrade dependencies. It gets out of control if you try and compile everything. But what if your distro''s RPMs are outdated? There is a magical thing called a source RPM. Get a source RPM of the outdated package, compile it using rpmbuild (don''t know how to use rpmbuild? `man rpmbuild''), and install the binary RPM the was built via rpmbuild:
</p>
<p>rpm -ivh --force package.arch.rpm
</p>
<p>If updating outdated dependencies doesn''t work, proceed to III.3.
</p>
<hr/>
III.3 - I''m Hopeless!
<hr/>

<p>If it seems as though you are hopeless, the stubborn donkey of a desklet you are trying to run might not support the version of gDesklets you have. If this is the case, in the wise words of pycage, ""email the author"".</p>
', '1');
INSERT INTO `gd_docs` (`doc_id`, `doc_author`, `doc_email`, `doc_title`, `doc_text`, `doc_released`) VALUES('5', 'chrisime', 'chrisime@gnome-de.org', 'gDesklets'' Deprendencies', 'To succesfully run gDesklets, you''ll need to install additional packages<br />
on our system. Distributions like Debian, Fedora or SuSE already have<br />
(most of) them included in their CD set or can be downloaded.<br />
<br />
The following packages are needed to run gDesklets:<br />
<br />
python, at least version 2.3<br />
python-gtk2, at least version 2.4. Older versions won''t work!<br />
python-gnome2, at least version 2.6<br />
python-pyorbit, version 2.0.1<br />
<br />
librsvg2, at least version 2.6<br />
libgtop2, at least version 2.8<br />
<br />
Naturally, all gnome dependencies have to be fulfilled!<br />
<br />
<br />
If you want to compile gDesklets:<br />
<br />
python-dev<br />
python-gtk2-dev<br />
python-gnome2-dev<br />
<br />
librsvg2-dev<br />
libgtop2-dev<br />
<br />
Additionally, the gnome development packages.<br />
<br />
Since v0.33 we removed the SWIG dependency from gDesklets.<br />
<br />
', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('8', 'devilx', 'devilx33@hotmail.com', 'Why doesn''t gdesklets work with my window manager?', 'You need an EWMH compliant WM (metacity, xfwm4, sawfish + patch).', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('7', 'devilx', 'devilx33@hotmail.com', 'How can I move my gDesklets?', 'Use the middle mouse button (also called 3rd mouse button).', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('9', 'devilx', 'devilx33@hotmail.com', 'Which versions of python* do I need to run gDesklets? ', 'Try to install the most recent versions (python 2.3, python-gnome 2.6 and python-gtk 2.4).', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('10', 'devilx', 'devilx33@hotmail.com', 'Why does gdesklets need so much CPU time?', 'We are currently working on that. There are many parts of the code which have to be improved in that respect. We''ve already marked some lines which cause it.', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('11', 'devilx', 'devilx33@hotmail.com', 'Why does gdesklets need so much RAM?', 'This mainly results from memory leaks in python-gtk/gnome. We''re trying to work around those bugs. Future version of python-g* will have less leaks!', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('12', 'devilx', 'devilx33@hotmail.com', 'When I start gDesklets, nothing happens.', 'You need to start a display; it''s automatically added then.', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('13', 'devilx', 'devilx33@hotmail.com', 'Nautilus 2.4 doesn''t want to start any displays.', 'This is a known ""bug"" in nautilus, it tries to look at the content of a file instead of the extension (like previous nautilus versions).', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('14', 'devilx', 'devilx33@hotmail.com', 'I''ve installed python2.2 and python2.3 on my system. Does that matter?', 'Please *NEVER* install more than one python package on your system. Most errors are the result of that!', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('15', 'devilx', 'devilx33@hotmail.com', 'Why does gDesklets eat so much memory (especially on a Linux 2.6 kernel)?', 'It doesn''t. You''re just looking at the wrong values.<br />
The RSS entry tells you how many memory is really used. SIZE is about virtual memory that would be used if every thread had its own private memory.', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('16', 'devilx', 'devilx33@hotmail.com', 'Why do my desklets all have a solid background?', 'gDesklets can run in two modes: real translucency (e.g. on the Xorg >= 6.8) or pseudo-transparency. Since real translucency is a new thing, most transparent Linux applications use pseudo-transparency. For pseudo-transparency, a portion of the background image is copied into the application''s window. To make this possible, the program setting the background must leave a hint about the used background. You can see if there''s a hint by calling<br />
<br />
xprop -root | grep PMAP_ID<br />
<br />
in a shell. Most environments like GNOME, KDE and XFCE behave correctly. You can also set the background using Esetroot.', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('32', 'chrisime', 'chrisime@gnome-de.org', 'Gdk-WARNING **: Couldn''t match property type STRING to UTF8_STRING ', 'If you got a warning which looks like this:<br />
<br />
Gdk-WARNING **: Couldn''t match property type STRING to UTF8_STRING<br />
<br />
your window manager isn''t EWMH compliant.<br />
See also: http://gnomesupport.org/forums/viewtopic.php?t=8600', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('18', 'devilx', 'devilx33@hotmail.com', 'gDesklets says that it can''t connect to gdesklets-daemon!', 'This either means that:<br />
<br />
    * gdesklets-daemon isn''t executable. Locate the file and ""chmod 755"" it.<br />
    * Any other severe problem occurred (a module or a C library couldn''t be loaded). Check the log file in ~/.gdesklets to see what''s wrong.<br />
', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('19', 'devilx', 'devilx33@hotmail.com', 'gDesklets doesn''t start at all!', 'Something bad happened, which shouldn''t happen ;-) Check you log file in ~/.gdesklets. It will tell you what went wrong!', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('20', 'devilx', 'devilx33@hotmail.com', 'Can I use gDesklets on Fluxbox/Openbox/Blackbox/Xfce/etc?', 'Yes you can.', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('21', 'devilx', 'devilx33@hotmail.com', 'What version of gDesklets is needed to support inline scrips?', 'gDesklets version 0.30 is at least needed to support inline-scripting.', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('22', 'devilx', 'devilx33@hotmail.com', 'How to I make a display to be on top?', 'Open the .display file with an editor and search for a line like this: <display window-flags=""sticky, below"" /><br />
Now replace below with above and the display will be on top.', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('23', 'devilx', 'devilx33@hotmail.com', 'What does this mean: (gDesklets:16081): Gdk-CRITICAL **: ...', 'file gdkpixbuf-drawable.c: line 1271 (gdk_pixbuf_get_from_drawable): assertion `src_x + width <= src_width && src_y + height <= src_height'' failed<br />
This error is because of a bug in pyxdg. You have to be patient till it''s removed or use hardcoded image patterns in your starters.', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('24', 'devilx', 'devilx33@hotmail.com', 'How do I start gDesklets on Gnome-Startup automaticly?', 'Open the Gnome Menu. Select ""Applications"" -> ""Desktop Prefrences"" -> ""Advanced"" click on ""Sessions"". Then open the ""Startup Programs""-Tab and click on ""Add"". Now just set gdesklets as ""Startup command"" and click on ""Ok"".', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('25', 'devilx', 'devilx33@hotmail.com', 'Why doesn''t my Rhythmlet work?', 'Rhythmlet needs Python 2.3 to work. Check your Python version and upgrade if needed.', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('26', 'devilx', 'devilx33@hotmail.com', 'How can I fix gnome.ui and bonobo.ui errors?', 'There errors just happen, if you haven''t installed some python bindings.', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('27', 'devilx', 'devilx33@hotmail.com', 'Why does GmailCheck stopped working?', 'Maybe you have got an old GmailCheck version. Older versions doesn''t work anymore because of the Gmail Protocol changes Google made. Newer versions started using the libgmail which uses an up-to-date protocol. Please upgrade your GmailCheck display', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('28', 'devilx', 'devilx33@hotmail.com', 'Why doesn''t ""Sticky Notes"" work with my gDesklets 0.26 (or lower)?', 'The ""Sticky Notes"" desklet is not meant to work with gDesklets 0.26. It uses the new version, 0.30. If you really want/need to use ""Sticky Notes"", upgrade your gDesklets version, else just don''t use it. You could take the Memo-desklet instead.', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('29', 'devilx', 'devilx33@hotmail.com', 'RPM Error: gdesklets-display is needed by gdesklets-x.xx.x-xxxx ?', 'You could try to install the RPM without take care of dependencies, by using the --nodeps parameter.', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('30', 'devilx', 'devilx33@hotmail.com', 'What means ""ImportError: No module named ...""?', 'It means that you''re missing a specific python binding. You''ll need to install it to be able to use the desklet.', '1');
INSERT INTO `gd_faq` (`faq_id`, `faq_author`, `faq_email`, `faq_title`, `faq_text`, `faq_released`) VALUES('31', 'devilx', 'devilx33@hotmail.com', 'I have a new Desklet idea, can I post it anywhere?', 'Yes you can! The gDesklets Forum provides a thread for new Desklet ideas.', '1');
INSERT INTO `gd_modules` (`mod_name`, `mod_url`, `mod_path`, `mod_access`, `mod_desc`) VALUES('listfaq', 'show', 'listfaq', '0', 'This Module is needed for the FAQ entry listing. If you remove it, the whole site will be useless.');
INSERT INTO `gd_modules` (`mod_name`, `mod_url`, `mod_path`, `mod_access`, `mod_desc`) VALUES('submit', 'submit', 'submit', '0', 'The Submission Module allows anonymous users to submit FAQ entries. The FAQ entries won''t be released until a moderator releases them.');
INSERT INTO `gd_modules` (`mod_name`, `mod_url`, `mod_path`, `mod_access`, `mod_desc`) VALUES('login', 'login', 'login', '0', 'The Login Module is needed by Moderators. Do not remove this module!');
INSERT INTO `gd_modules` (`mod_name`, `mod_url`, `mod_path`, `mod_access`, `mod_desc`) VALUES('admin_pwd', 'admin/pwd', 'admin/admin_pwd', '1', 'The Account Password Manager provides you, to change the password for your account anytime.');
INSERT INTO `gd_modules` (`mod_name`, `mod_url`, `mod_path`, `mod_access`, `mod_desc`) VALUES('admin_site', 'admin/site', 'admin/admin_site', '1', 'The Site Administration Module is needed for the general site configuration.');
INSERT INTO `gd_modules` (`mod_name`, `mod_url`, `mod_path`, `mod_access`, `mod_desc`) VALUES('admin_faq', 'admin/faq', 'admin/admin_faq', '1', 'The FAQ Administration Module allows you to release pending FAQs and also to delete them.');
INSERT INTO `gd_modules` (`mod_name`, `mod_url`, `mod_path`, `mod_access`, `mod_desc`) VALUES('admin', 'admin', 'admin/admin', '1', 'The Admin Control Center from which the whole site can be configured.');
INSERT INTO `gd_modules` (`mod_name`, `mod_url`, `mod_path`, `mod_access`, `mod_desc`) VALUES('admin_modules', 'admin/modules', 'admin/admin_modules', '1', 'This Module helps you configuring existing and setting up new Modules for the website.');
INSERT INTO `gd_modules` (`mod_name`, `mod_url`, `mod_path`, `mod_access`, `mod_desc`) VALUES('admin_users', 'admin/users', 'admin/admin_users', '1', 'This Module allows you the administration of privileged users on the site.');
INSERT INTO `gd_modules` (`mod_name`, `mod_url`, `mod_path`, `mod_access`, `mod_desc`) VALUES('docs', 'docs', 'docs', '0', 'This Module provides listing of documentations.
');
INSERT INTO `gd_modules` (`mod_name`, `mod_url`, `mod_path`, `mod_access`, `mod_desc`) VALUES('admin_docs', 'admin/docs', 'admin/admin_docs', '1', 'The Document Administration Module allows you to release and delete submitted documents.');
INSERT INTO `gd_modules` (`mod_name`, `mod_url`, `mod_path`, `mod_access`, `mod_desc`) VALUES('dependencies', 'deps', 'dependencies', '0', 'A dependency description by chrisime.');
INSERT INTO `gd_modules` (`mod_name`, `mod_url`, `mod_path`, `mod_access`, `mod_desc`) VALUES('search', 'search', 'search', '0', 'This Module provides searching for information on this site through google.com.');
INSERT INTO `gd_modules` (`mod_name`, `mod_url`, `mod_path`, `mod_access`, `mod_desc`) VALUES('admin_edit', 'admin/edit', 'admin/admin_edit', '1', 'This Module allows Moderators to edit entries.');
