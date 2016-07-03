#! /bin/sh

#
# Creates HTML from docbook files using the yelp XSL stylesheets.
#


if [ -z "$1" -o -z "$2" ]; then
  echo Usage: `basename $0` bookfile output-directory
  exit 1
fi


INPUT=$1
DIR=`dirname $INPUT`
TMP=$DIR/tmp.xml
DEST=$2

# location of the stylesheets
#XSL=/usr/share/xml/gnome/xslt/docbook/html/db2html.xsl
XSL=./yelp/db2html.xsl


#
# Just make sure to be sure that everything in DEST is going to be deleted
#
echo -n "Do you REALLY want to delete everything in $DEST ?? (yes/No) " 
read GOAHEAD
if [ "$GOAHEAD" != "yes" ] ; then
  echo Aborting!
  exit 1
fi


#
# create HTML
#
echo "cleaning output-directory"
rm -rf $DEST/*


#
# create HTML
#
echo "creating HTML"
xmllint --xinclude $1 >$TMP
xsltproc -v -o $DEST/index.html $XSL $TMP


#
# remove navbar in index.html, set target for <a href="...">
#
echo "altering index.html"
cp $DEST/index.html $DEST/index2.html.temp
cat $DEST/index.html \
    | tr "\n" "\b" \
    | sed -e "s/<div class=\"navbar-bottom\">.*<\/div>//" \
    | sed -e "s/<a/<a target=\"main\"/g" \
    | tr "\b" "\n" \
  > $DEST/index.html.temp
cp $DEST/index.html.temp $DEST/toc.html


#
# replace stylesheet, remove Contents link
#
echo "replacing stylesheet"
for F in `ls $DEST/*.html`; do
#      | sed -e "s/; charset=UTF-8\">/; charset=ISO8859-1\">/" \
#      | iconv -f ISO-8859-1 -t UTF-8 \
  cat $F \
      | sed -e "s/%;/\&/g" \
      | tr "\n" "\b" \
      | sed -e "s/<style .*<\/style>/<link rel=\"stylesheet\" type=\"text\/css\" href=\"style.css\">/" \
      | tr "\b" "\n" \
      | sed -e "s/<td .*<a href=.*>Contents<\/a><\/td>//" \
      | sed -e "s/<td .*<a href=.*>About This Book<\/a><\/td>//" \
    > $F.tmp
  mv $F.tmp $F
done


#
# copy graphics
#
echo "copying graphics"
cp -r $DIR/gfx $DEST/gfx
cp -r /usr/share/yelp/icons $DEST/images
rename "yelp-icon-" "" $DEST/images/*
mkdir -p $DEST/images/icons
cp /usr/share/icons/gnome/32x32/mimetypes/package.png $DEST/images/icons
cp /usr/share/icons/gnome/32x32/mimetypes/document.png $DEST/images/icons
rm -rf $DEST/gfx/CVS


#
# setup index.html
#
read -p "Your name: " NAME
cat >$DEST/index.html << EOF
<html>
<head><title>gDesklets Developer's Book</title></head>
<body>
  <h2>The gDesklets Developer's Book</h2>

  <p>The book can be read online or be downloaded for reading offline.</p>

  <p><img src="./images/icons/document.png">
     <a href="book.html">Read online</a></p>

  <p><img src="./images/icons/package.png">
     <a href="develbook.tar.bz2">Download HTML for reading offline</a></p>

  <hr>
  <font size="2"><p>Last updated on `date -R` by $NAME.</p></font>
</body>
</html>
EOF


#
# setup book.html
#
cat >$DEST/book.html << EOF
<frameset cols="30%,*">
  <frame src="toc.html">
  <frame src="titlepage.html" name="main">
</frameset>
EOF


#
# the stylesheet
#
echo "creating stylesheet"
cat >$DEST/style.css << EOF
/* CSS stylesheet for gDesklets color style */ 
/* by Martin Grimme  <martin@gdesklets.org> */ 
 
body * {  
  background-color: #ffffff; 
  color: black; 
  font-family: Sans-Serif; 
  font-size: 1.0em; 
} 
 
div.toc * { font-weight: bold; } 
 
a:link, a:link * { color: #5a799c; } 
a:visited, a:visited * { color: darkred; } 
a:hover, a:hover * { color: white; background-color: #5a799c; } 
 
ul { list-style-type: square; } 
 
div.admonition {  
  border-color: black; 
  border-style: solid; 
  border-width: thin; 
} 
 
div.admonition * { 
  font-size: 8pt; 
  background-color: #fff3ce; 
} 
 
div.programlisting * {  
  padding: 1ex; 
  font-family: Monospace; 
  font-weight: bold; 
  background-color: fff3ce; 
} 
 
div.navbar-bottom {  
  margin-top: 1em; 
  border-color: black; 
  border-style: solid; 
  border-width: thin;   
} 
 
div.navbar-bottom * {  
  padding-left: 1pt; 
  padding-right: 1pt; 
  color: white; 
  font-weight: bold; 
  background-color: #5a799c; 
} 
 
div.navbar-bottom a:link { color: white; } 
div.navbar-bottom a:visited { color: white; } 
div.navbar-bottom a:hover { color: black; background-color: white; } 
 
span.emphasize, span.literal, span.parameter, span.property { font-weight: bold\
; } 
 
h1 { font-size: 1.6em; font-weight: bold; } 
h2 { font-size: 1.4em; font-weight: bold; } 
h3 { font-size: 1.2em; font-weight: bold; } 
 
tt { font-family: monospace; } 

EOF

