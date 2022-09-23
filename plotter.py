# Copyright 2022 Rampart Communications

import argparse

import numpy as np
import matplotlib.pyplot as plt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        "Plot constellation from fc32 file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('filename')
    args = vars(parser.parse_args())

    fid = open(args['filename'], 'rb')
    data = np.fromfile(fid, dtype=np.complex64)

    fid.close()

    plt.figure()
    plt.plot(np.real(data), np.imag(data), '.')
    plt.xlim([-2, 2])
    plt.ylim([-2, 2])
    plt.show()
