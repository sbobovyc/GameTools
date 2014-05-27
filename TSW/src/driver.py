import os
import sys
import idx
import filemap

if __name__ == "__main__":
    filepath = sys.argv[1]
    dirname = os.path.dirname(filepath) 
    idx_file = idx.IDX_index_file(filepath)
    idx_file.dump()

    # extract filemap from rdbdata 
    mapfile_index = idx_file.get_indeces(1000010)[1]
    print "Filemap found at index", mapfile_index
    filename, offset, size = idx_file.get_entry_details(mapfile_index)

    data = None
    with open(os.path.join(dirname, filename), "rb") as f:
        f.seek(offset)
        data = f.read(size)
   
    with open("filemap.bin", "wb") as f:
        f.write(data)
        f.flush()

    # once filemap is dumped to disk, parse it
    fm = filemap.mapping("filemap.bin")
    fm.dump()

    # search for all files in filemap and dump them
    for tp in fm.types:
        if tp.num_entries > 0:
            print tp.RDB_type
            current_type_dict = idx_file.get_indeces(tp.RDB_type)
            for fl in tp.filename_entries:
                try:
                    index = current_type_dict[fl.RDB_id]
                    filename, offset, size = idx_file.get_entry_details(index)
                    try:
                        filepath = os.path.join(dirname, filename)
                        with open(filepath, "rb") as f:
                            f.seek(offset)
                            data = f.read(size)
                        output_filepath = os.path.join("out", fl.filename)
                        if not os.path.exists("out"):
                            os.makedirs("out")
                        with open(output_filepath, "wb") as f:
                            f.write(data)
                            f.flush()
                    except IOError:
                        # rdbdata file does not exist
                        pass
                    
                except KeyError:
                    pass
                    #print "Index file is missing RDB id %i, file name %s" % (fl.RDB_id, fl.filename)            
        
