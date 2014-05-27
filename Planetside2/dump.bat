set PS2PATH=.\Assets
set OUTPATH=.\dump
set PARAMS=-f "txt" 
for %%i in (%PS2PATH%) do python ps2_unpack.py %PARAMS% "%%i" %OUTPATH%
