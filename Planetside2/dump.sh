FILES=Assets/Assets_*
OUTPATH=./dump
PARAMS=-f "adr"

for f in $FILES
do
	python ps2_unpack.py -f "adr" $f $OUTPATH
done
