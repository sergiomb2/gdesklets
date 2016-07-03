#! /bin/sh

DIR=`dirname $0`
xmllint --xinclude $DIR/book.xml >$DIR/xibook.xml
yelp ghelp://$PWD/$DIR/xibook.xml
