-- phpMyAdmin SQL Dump
-- version 2.6.0-pl3
-- http://www.phpmyadmin.net
-- 
-- Host: localhost
-- Generation Time: Jan 06, 2005 at 05:05 PM
-- Server version: 4.0.23
-- PHP Version: 4.3.10-2
-- 
-- Database: `gdesklets`
-- 

-- --------------------------------------------------------

-- 
-- Table structure for table `gd_conf`
-- 

CREATE TABLE `gd_conf` (
  `conf_name` text NOT NULL,
  `conf_value` text NOT NULL
) TYPE=MyISAM;

-- 
-- Dumping data for table `gd_conf`
-- 

INSERT INTO `gd_conf` VALUES ('site_bottom', 'The official inofficial gDesklets Website');
INSERT INTO `gd_conf` VALUES ('site_menu', '<a href="?" target="_self">Home</a> |\r\n<a href="?mod=deps" target="_self">Dependencies</a> |\r\n<a href="?mod=show" target="_self">FAQ</a> |\r\n<a href="?mod=docs" target="_self">Documents</a> |\r\n<a href="?mod=search" target="_self">Search</a> |\r\n<a href="?mod=submit" target="_self">Submit</a>');

-- --------------------------------------------------------

-- 
-- Table structure for table `gd_desklets`
-- 

CREATE TABLE `gd_desklets` (
  `dl_id` int(11) NOT NULL auto_increment,
  `dl_author` text NOT NULL,
  `dl_email` text NOT NULL,
  `dl_www` text NOT NULL,
  `dl_title` text NOT NULL,
  `dl_text` text NOT NULL,
  `dl_sshot` text NOT NULL,
  `dl_file` text NOT NULL,
  `dl_dls` int(11) NOT NULL default '0',
  `dl_votes` int(11) NOT NULL default '0',
  `dl_votesvals` int(11) NOT NULL default '0',
  PRIMARY KEY  (`dl_id`)
) TYPE=MyISAM AUTO_INCREMENT=1 ;

-- 
-- Dumping data for table `gd_desklets`
-- 


-- --------------------------------------------------------

-- 
-- Table structure for table `gd_docs`
-- 

CREATE TABLE `gd_docs` (
  `doc_id` int(11) NOT NULL auto_increment,
  `doc_author` text NOT NULL,
  `doc_email` text NOT NULL,
  `doc_title` text NOT NULL,
  `doc_text` longtext NOT NULL,
  `doc_released` tinyint(4) NOT NULL default '0',
  PRIMARY KEY  (`doc_id`)
) TYPE=MyISAM AUTO_INCREMENT=4 ;

-- 
-- Dumping data for table `gd_docs`
-- 

INSERT INTO `gd_docs` VALUES (3, 'a monkey', 'thechimp@earthlink.net', 'gDesklets General User''s Guide', '<hr/>\r\ngDesklets general user''s guide by a monkey (<a href="mailto:thechimp@earthlink.net">thechimp@earthlink.net</a>)\r\nVersion 0.1\r\n<hr/>\r\n\r\n<p>Table of Contents\r\n</p>\r\n<p>I - Getting Started\r\n</p>\r\n<p>  I.1 - Downloading gDesklets<br/>\r\n  I.2 - Installation<br/>\r\n  I.3 - Firing up gDesklets\r\n</p>\r\n<p>II - Desklets\r\n</p>\r\n<p>  II.1 - Downloading Desklets<br/>\r\n  II.2 - Installing a Desklet''s Sensor<br/>\r\n  II.3 - Running the Display File\r\n</p>\r\n<p>III - Troubleshooting\r\n</p>\r\n<p>  III.1 - Do You Have Outdated Dependencies?\r\n  III.2 - Upgrading Dependencies<br/>\r\n  III.3 - I''m Hopeless!\r\n</p>\r\n<hr/>\r\nI - Getting Started\r\n<hr/>\r\n\r\n<hr/>\r\nI.1 - Downloading gDesklets\r\n<hr/>\r\n\r\n<p>You can download the latest version of gDesklets'' source code here:\r\n</p>\r\n<p><a href="http://www.pycage.de/software_gdesklets.html">http://www.pycage.de/software_gdesklets.html</a>\r\n</p>\r\n<p>Unpack the compressed tar.bz2 file like this:\r\n</p>\r\n<p>tar -jxvf gDesklets-&lt;version&gt;.tar.bz2\r\n</p>\r\n<hr/>\r\nI.2 - Installation\r\n<hr/>\r\n\r\n<p>Hold your horses, there. First read the README file included in the folder you just unpacked. This will tell you how to install compile and install gDesklets in the first half of step 3. I''m not going to recite the README file for you, so do what I say, read it.\r\n</p>\r\n<hr/>\r\nI.3 - Firing up gDesklets\r\n<hr/>\r\n\r\n<p>Once you''ve installed gDesklets as the first half of step 3 in the README told you, get to the command line, cross your fingers, and type\r\n</p>\r\n<p>gdesklets start\r\n</p>\r\n<p>If you get a timeout error when connecting to the gDesklets daemon, this generally means that you do not have the proper dependencies of gDesklets installed. Browse through step 2 of the README file to make sure that you have all of gDesklets'' dependencies installed at the proper versions. One mistake I made was trying to run gDesklets 0.32 with python-gnome 2.0.0. Also, make sure that you have the dependencies of gDesklets itself installed, not only the requirements for compiling gDesklets, e.g. pygtk itself instead of your distro''s pygtk-devel package.\r\n</p>\r\n<p>Once there are no errors after typing `gdesklets start'', this means you''ve successfully fired up gDesklets. But don''t get worried if you don''t see a bunch of eye-candy popping up all over your desktop, installing desklets comes later.\r\n</p>\r\n<hr/>\r\nII - Desklets\r\n<hr/>\r\n\r\n<hr/>\r\nII.1 - Downloading Desklets\r\n<hr/>\r\n\r\n<p>There are tons of desklets available for free at\r\n</p>\r\n<p><a href="http://gdesklets.gnomedesktop.org/">http://gdesklets.gnomedesktop.org/</a>\r\n</p>\r\n<p>Unpack a desklet like this:\r\n</p>\r\n<p>tar -jxvf &lt;desklet&gt;.tar.bz2\r\n</p>\r\n<hr/>\r\nII.2 - Installing a Desklet''s Sensor and Controls\r\n<hr/>\r\n\r\n<p>You should be able to skip this step, now that sensors are deprecated. But if you see a sensor or a Install_&lt;desklet&gt;_Sensor.bin file, you should go through this step. You should copy sensors to ~/.gdesklets/Sensors/ using the `cp'' command (cp --help), or else run the installer:\r\n</p>\r\n<p>cd &lt;desklet directory&gt;<br/>\r\n./Install_&lt;desklet&gt;_Sensor.bin\r\n</p>\r\n<ul>\r\n  <li>NOTE: You should not be root when doing this.\r\n\r\n</li></ul>\r\n<p>If all goes well, you will get a message saying "The sensor has been installed successfully. gDesklets is now able to use it."\r\n</p>\r\n<p>Install a desklet''s controls by using the cp command to copy them to ~/.gdesklets/Controls/\r\n</p>\r\n<hr/>\r\nII.3 - Running the Display File\r\n<hr/>\r\n\r\n<p>The README will tell you how to open a display file via gDesklets in the very beginning of step 5.1.\r\n</p>\r\n<hr/>\r\nIII - Troubleshooting\r\n<hr/>\r\n\r\n<hr/>\r\nIII.1 - Do You Have Outdated Dependencies?\r\n<hr/>\r\n\r\n<ul>\r\n  <li>Note: Only people whose distro has an RPM-based package management system should proceed. I don''t know anything about other distros like Debian, so I won''t speak for them.\r\n\r\n</li></ul>\r\n<p>If you think you may have an outdated dependency, check if you do like this:\r\n</p>\r\n<p>rpm -qi &lt;package name&gt;\r\n</p>\r\n<p>If this shows that you have an outdated dependency, you should proceed to III.2.\r\n</p>\r\n<hr/>\r\nIII.2 - Upgrading Dependencies\r\n<hr/>\r\n\r\n<p>Try to stick to using RPMs to upgrade dependencies. It gets out of control if you try and compile everything. But what if your distro''s RPMs are outdated? There is a magical thing called a source RPM. Get a source RPM of the outdated package, compile it using rpmbuild (don''t know how to use rpmbuild? `man rpmbuild''), and install the binary RPM the was built via rpmbuild:\r\n</p>\r\n<p>rpm -ivh --force package.arch.rpm\r\n</p>\r\n<p>If updating outdated dependencies doesn''t work, proceed to III.3.\r\n</p>\r\n<hr/>\r\nIII.3 - I''m Hopeless!\r\n<hr/>\r\n\r\n<p>If it seems as though you are hopeless, the stubborn donkey of a desklet you are trying to run might not support the version of gDesklets you have. If this is the case, in the wise words of pycage, "email the author".</p>\r\n', 1);

-- --------------------------------------------------------

-- 
-- Table structure for table `gd_faq`
-- 

CREATE TABLE `gd_faq` (
  `faq_id` int(11) NOT NULL auto_increment,
  `faq_author` text NOT NULL,
  `faq_email` text NOT NULL,
  `faq_title` text NOT NULL,
  `faq_text` text NOT NULL,
  `faq_released` smallint(6) NOT NULL default '0',
  PRIMARY KEY  (`faq_id`)
) TYPE=MyISAM AUTO_INCREMENT=32 ;

-- 
-- Dumping data for table `gd_faq`
-- 

INSERT INTO `gd_faq` VALUES (8, 'devilx', 'devilx33@hotmail.com', 'Why doesn''t gdesklets work with my window manager?', 'You need an EWMH compliant WM (metacity, xfwm4, sawfish + patch).', 1);
INSERT INTO `gd_faq` VALUES (7, 'devilx', 'devilx33@hotmail.com', 'How can I move my gDesklets?', 'Use the middle mouse button (also called 3rd mouse button).', 1);
INSERT INTO `gd_faq` VALUES (9, 'devilx', 'devilx33@hotmail.com', 'Which versions of python* do I need to run gDesklets? ', 'Try to install the most recent versions (python 2.2.x, python-gnome 1.99.17).', 1);
INSERT INTO `gd_faq` VALUES (10, 'devilx', 'devilx33@hotmail.com', 'Why does gdesklets need so much CPU time?', 'We are currently working on that. There are many parts of the code which have to be improved in that respect. We''ve already marked some lines which cause it.', 1);
INSERT INTO `gd_faq` VALUES (11, 'devilx', 'devilx33@hotmail.com', 'Why does gdesklets need so much RAM?', 'This mainly results from memory leaks in python-gtk/gnome. We''re trying to work around those bugs. Future version of python-g* will have less leaks!', 1);
INSERT INTO `gd_faq` VALUES (12, 'devilx', 'devilx33@hotmail.com', 'When I start gDesklets, nothing happens.', 'You need to start a display; it''s automatically added then.', 1);
INSERT INTO `gd_faq` VALUES (13, 'devilx', 'devilx33@hotmail.com', 'Nautilus 2.4 doesn''t want to start any displays.', 'This is a known "bug" in nautilus, it tries to look at the content of a file instead of the extension (like previous nautilus versions).', 1);
INSERT INTO `gd_faq` VALUES (14, 'devilx', 'devilx33@hotmail.com', 'I''ve installed python2.2 and python2.3 on my system. Does that matter?', 'Please *NEVER* install more than one python package on your system. Most errors are the result of that!', 1);
INSERT INTO `gd_faq` VALUES (15, 'devilx', 'devilx33@hotmail.com', 'Why does gDesklets eat so much memory (especially on a Linux 2.6 kernel)?', 'It doesn''t. You''re just looking at the wrong values.<br />\r\nThe RSS entry tells you how many memory is really used. SIZE is about virtual memory that would be used if every thread had its own private memory.', 1);
INSERT INTO `gd_faq` VALUES (16, 'devilx', 'devilx33@hotmail.com', 'Why do my desklets all have a solid background?', 'gDesklets can run in two modes: real translucency (e.g. on the Xorg >= 6.8) or pseudo-transparency. Since real translucency is a new thing, most transparent Linux applications use pseudo-transparency. For pseudo-transparency, a portion of the background image is copied into the application''s window. To make this possible, the program setting the background must leave a hint about the used background. You can see if there''s a hint by calling<br />\r\n<br />\r\nxprop -root | grep PMAP_ID<br />\r\n<br />\r\nin a shell. Most environments like GNOME, KDE and XFCE behave correctly. You can also set the background using Esetroot.', 1);
INSERT INTO `gd_faq` VALUES (17, 'devilx', 'devilx33@hotmail.com', 'gDesklets doesn''t start at all!', 'Something bad happened, which shouldn''t happen ;-) Check you log file in ~/.gdesklets. It will tell you what went wrong!', 1);
INSERT INTO `gd_faq` VALUES (18, 'devilx', 'devilx33@hotmail.com', 'gDesklets says that it can''t connect to gdesklets-daemon!', 'This either means that:<br />\r\n<br />\r\n    * gdesklets-daemon isn''t executable. Locate the file and "chmod 755" it.<br />\r\n    * Any other severe problem occurred (a module or a C library couldn''t be loaded). Check the log file in ~/.gdesklets to see what''s wrong.<br />\r\n', 1);
INSERT INTO `gd_faq` VALUES (19, 'devilx', 'devilx33@hotmail.com', 'gDesklets doesn''t start at all!', 'Something bad happened, which shouldn''t happen ;-) Check you log file in ~/.gdesklets. It will tell you what went wrong!', 1);
INSERT INTO `gd_faq` VALUES (20, 'devilx', 'devilx33@hotmail.com', 'Can I use gDesklets on Fluxbox/Openbox/Blackbox/Xfce/etc?', 'Yes you can.', 1);
INSERT INTO `gd_faq` VALUES (21, 'devilx', 'devilx33@hotmail.com', 'What version of gDesklets is needed to support inline scrips?', 'gDesklets version 0.30 is at least needed to support inline-scripting.', 1);
INSERT INTO `gd_faq` VALUES (22, 'devilx', 'devilx33@hotmail.com', 'How to I make a display to be on top?', 'Open the .display file with an editor and search for a line like this: <display window-flags="sticky, below" /><br />\r\nNow replace below with above and the display will be on top.', 1);
INSERT INTO `gd_faq` VALUES (23, 'devilx', 'devilx33@hotmail.com', 'What does this mean: (gDesklets:16081): Gdk-CRITICAL **: ...', 'file gdkpixbuf-drawable.c: line 1271 (gdk_pixbuf_get_from_drawable): assertion `src_x + width <= src_width && src_y + height <= src_height'' failed<br />\r\nThis error is because of a bug in pyxdg. You have to be patient till it''s removed or use hardcoded image patterns in your starters.', 1);
INSERT INTO `gd_faq` VALUES (24, 'devilx', 'devilx33@hotmail.com', 'How do I start gDesklets on Gnome-Startup automaticly?', 'Open the Gnome Menu. Select "Applications" -> "Desktop Prefrences" -> "Advanced" click on "Sessions". Then open the "Startup Programs"-Tab and click on "Add". Now just set gdesklets as "Startup command" and click on "Ok".', 1);
INSERT INTO `gd_faq` VALUES (25, 'devilx', 'devilx33@hotmail.com', 'Why doesn''t my Rhythmlet work?', 'Rhythmlet needs Python 2.3 to work. Check your Python version and upgrade if needed.', 1);
INSERT INTO `gd_faq` VALUES (26, 'devilx', 'devilx33@hotmail.com', 'How can I fix gnome.ui and bonobo.ui errors?', 'There errors just happen, if you haven''t installed some python bindings.', 1);
INSERT INTO `gd_faq` VALUES (27, 'devilx', 'devilx33@hotmail.com', 'Why does GmailCheck stopped working?', 'Maybe you have got an old GmailCheck version. Older versions doesn''t work anymore because of the Gmail Protocol changes Google made. Newer versions started using the libgmail which uses an up-to-date protocol. Please upgrade your GmailCheck display', 1);
INSERT INTO `gd_faq` VALUES (28, 'devilx', 'devilx33@hotmail.com', 'Why doesn''t "Sticky Notes" work with my gDesklets 0.26 (or lower)?', 'The "Sticky Notes" desklet is not meant to work with gDesklets 0.26. It uses the new version, 0.30. If you really want/need to use "Sticky Notes", upgrade your gDesklets version, else just don''t use it. You could take the Memo-desklet instead.', 1);
INSERT INTO `gd_faq` VALUES (29, 'devilx', 'devilx33@hotmail.com', 'RPM Error: gdesklets-display is needed by gdesklets-x.xx.x-xxxx ?', 'You could try to install the RPM without take care of dependencies, by using the --nodeps parameter.', 1);
INSERT INTO `gd_faq` VALUES (30, 'devilx', 'devilx33@hotmail.com', 'What means "ImportError: No module named ..."?', 'It means that you''re missing a specific python binding. You''ll need to install it to be able to use the desklet.', 1);
INSERT INTO `gd_faq` VALUES (31, 'devilx', 'devilx33@hotmail.com', 'I have a new Desklet idea, can I post it anywhere?', 'Yes you can! The gDesklets Forum provides a thread for new Desklet ideas.', 1);

-- --------------------------------------------------------

-- 
-- Table structure for table `gd_modules`
-- 

CREATE TABLE `gd_modules` (
  `mod_name` text NOT NULL,
  `mod_url` text NOT NULL,
  `mod_path` text NOT NULL,
  `mod_access` tinyint(4) NOT NULL default '0',
  `mod_desc` text NOT NULL
) TYPE=MyISAM;

-- 
-- Dumping data for table `gd_modules`
-- 

INSERT INTO `gd_modules` VALUES ('listfaq', 'show', 'listfaq', 0, 'This Module is needed for the FAQ entry listing. If you remove it, the whole site will be useless.');
INSERT INTO `gd_modules` VALUES ('submit', 'submit', 'submit', 0, 'The Submission Module allows anonymous users to submit FAQ entries. The FAQ entries won''t be released until a moderator releases them.');
INSERT INTO `gd_modules` VALUES ('login', 'login', 'login', 0, 'The Login Module is needed by Moderators. Do not remove this module!');
INSERT INTO `gd_modules` VALUES ('admin_pwd', 'admin/pwd', 'admin/admin_pwd', 1, 'The Account Password Manager provides you, to change the password for your account anytime.');
INSERT INTO `gd_modules` VALUES ('admin_site', 'admin/site', 'admin/admin_site', 1, 'The Site Administration Module is needed for the general site configuration.');
INSERT INTO `gd_modules` VALUES ('admin_faq', 'admin/faq', 'admin/admin_faq', 1, 'The FAQ Administration Module allows you to release pending FAQs and also to delete them.');
INSERT INTO `gd_modules` VALUES ('admin', 'admin', 'admin/admin', 1, 'The Admin Control Center from which the whole site can be configured.');
INSERT INTO `gd_modules` VALUES ('admin_modules', 'admin/modules', 'admin/admin_modules', 1, 'This Module helps you configuring existing and setting up new Modules for the website.');
INSERT INTO `gd_modules` VALUES ('admin_users', 'admin/users', 'admin/admin_users', 1, 'This Module allows you the administration of privileged users on the site.');
INSERT INTO `gd_modules` VALUES ('docs', 'docs', 'docs', 0, 'This Module provides listing of documentations.\r\n');
INSERT INTO `gd_modules` VALUES ('admin_docs', 'admin/docs', 'admin/admin_docs', 1, 'The Document Administration Module allows you to release and delete submitted documents.');
INSERT INTO `gd_modules` VALUES ('dependencies', 'deps', 'dependencies', 0, 'A dependency description by chrisime.');
INSERT INTO `gd_modules` VALUES ('search', 'search', 'search', 0, 'This Module provides searching this Site for information through google.com.');
INSERT INTO `gd_modules` VALUES ('admin_edit', 'admin/edit', 'admin/admin_edit', 1, 'This Module allows moderators to edit entries.');

-- --------------------------------------------------------

-- 
-- Table structure for table `gd_users`
-- 

CREATE TABLE `gd_users` (
  `usr_id` int(11) NOT NULL auto_increment,
  `usr_name` text NOT NULL,
  `usr_pwd` text NOT NULL,
  `usr_email` text NOT NULL,
  `usr_locked` tinyint(4) NOT NULL default '0',
  PRIMARY KEY  (`usr_id`)
) TYPE=MyISAM AUTO_INCREMENT=9 ;

-- 
-- Dumping data for table `gd_users`
-- 

INSERT INTO `gd_users` VALUES (1, 'devilx', 'ae85c391f2ea8f0212ee4b08738f1b00', 'devilx33@hotmail.com', 1);
INSERT INTO `gd_users` VALUES (6, 'chrisime', 'fef293486f24ee73618e626b8e0e5e37', 'chrisime@gnome.org', 0);
INSERT INTO `gd_users` VALUES (7, 'pycage', 'ee0de3d1bd5af169aaf93dd62c72ea56', 'martin@pycage.de', 0);
INSERT INTO `gd_users` VALUES (8, 'taz', '2ce7de3304d130517e91ccaae00ac668', 'benoit.dejean@placenet.org', 0);
