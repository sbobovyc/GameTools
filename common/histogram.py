import argparse
import os
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot byte histogram of any file.')
    parser.add_argument('filepath', nargs='?', help='File to analyze')
    args = parser.parse_args()

    with open(args.filepath, "rb") as f:
        x = np.fromfile(f, dtype=np.uint8)
        fig, ax = plt.subplots()
        plt.hist(x, bins=256, range=(0.0, 255.0), fc='k', ec='k')
        title = os.path.basename(args.filepath) + ", %i bytes" % os.stat(args.filepath).st_size
        ax.set_title(title)
        ax.set_xlim(0, 255)
        plt.show()
