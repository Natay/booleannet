

PYFILES=$1/*.py


for pyfile in $PYFILES
do
  2to3 -w -f all $pyfile

done
