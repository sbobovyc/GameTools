**Modding tools for Combat Mission**

Requirements

 - Python 2.7

To view the help message of scripts:  
python brz_magick.py -h

To extract a brz file:  
python brz_magick.py -x my_file.brz

To compress a directory with files into brz:  
python brz_magick.py -c mydir

To dump mdr file to OBJ and manifest:  
python unmdr.py crate1.mdr

To mutate mdr file:  
python mdr_mutator.py crate1_manifest.json --outdir "C:\Users\sbobovyc\Documents\Battlefront\Combat Mission\Black Sea\User Data\Mods"
