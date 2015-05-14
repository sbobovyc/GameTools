import argparse
import numpy as np
import matplotlib.pyplot as plt
import time
from pprint import pprint, pformat

cmaps = [('Sequential',     ['Blues', 'BuGn', 'BuPu',
                             'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd',
                             'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu',
                             'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd']),
         ('Sequential (2)', ['afmhot', 'autumn', 'bone', 'cool', 'copper',
                             'gist_heat', 'gray', 'hot', 'pink',
                             'spring', 'summer', 'winter']),
         ('Diverging',      ['BrBG', 'bwr', 'coolwarm', 'PiYG', 'PRGn', 'PuOr',
                             'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral',
                             'seismic']),
         ('Qualitative',    ['Accent', 'Dark2', 'Paired', 'Pastel1',
                             'Pastel2', 'Set1', 'Set2', 'Set3']),
         ('Miscellaneous',  ['gist_earth', 'terrain', 'ocean', 'gist_stern',
                             'brg', 'CMRmap', 'cubehelix',
                             'gnuplot', 'gnuplot2', 'gist_ncar',
                             'nipy_spectral', 'jet', 'rainbow',
                             'gist_rainbow', 'hsv', 'flag', 'prism'])]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tool that can unpack/pack Combat Mission brz files.', epilog='Color maps %s' % pformat(cmaps))
    parser.add_argument('filepath', nargs='?', help='File to analyze')
    parser.add_argument('--colormap', default='hot', help='Matplotlib color map')
    args = parser.parse_args()

    pprint(cmaps)

    f = args.filepath
    debug = False
    
    t1 = time.time()
    data = np.fromfile(f, np.dtype('u1'))
    t2 = time.time()
    print "Time reading from binary file: ",  t2-t1

    print "data shape", data.shape
    padded_data = np.resize(data, data.shape[0] + (8 - (data.shape[0] % 8)))
    print "padded data shape", padded_data.shape
    new_data = np.reshape(padded_data, (-1, 8))
    print "new_data shape", new_data.shape
    
    if debug:
        np.set_printoptions(formatter={'int':hex})
        print new_data
    
    # put the major ticks at the middle of each cell
    fig, ax = plt.subplots()
    mp = args.colormap
    t1 = time.time()
    ax.pcolormesh(new_data, cmap=mp)
    t2 = time.time()
    print "Time to plot: ",  t2-t1
    
    xlabels = map(lambda x: hex(x), range(0, 8))
    #print xlabels
    # put the major ticks at the middle of each cell
    ax.set_xticks(np.arange(new_data.shape[1])+0.5, minor=False)
    #ax.set_yticks(np.arange(new_data.shape[0])+0.5, minor=False)
    ax.set_xticklabels(xlabels, minor=False)
    
    # want a more natural, table-like display
    ax.invert_yaxis()
    ax.xaxis.tick_top()
    
    plt.show()
    
    
