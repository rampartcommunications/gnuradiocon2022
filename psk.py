# Copyright 2022 Rampart Communications

import sys
import os
import math
import cmath
import scipy
import numpy as np

from copy import deepcopy as copy

import argparse


class argparse_psk(argparse.ArgumentParser):
    """ Argparse wrapper to provide better help messages on error """
    def error(self, message):
        sys.stderr.write('Error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def bits_to_int(bits):
    """ Convert list of bits to integer """

    # Assumes MSB first
    vec = [2**(len(bits)-i-1) * bits[i] for i in range(len(bits))]
    return sum(vec)


def int_to_bits(val, N=None):
    """ Convert integer to list of bits """
    # Assumes MSB first

    # Special case that makes log angry
    if val == 0:
        return [0]

    # Required number of bits
    n = math.ceil(math.log2(val))
    if 2 ** n == val:
        n += 1

    # Check specified N value
    if N is None:
        N = n
    elif n > N:
        raise(Exception("Cannot represent %d in %d bits.  Needs %d bits" % (
            val, N, n)))

    # Use bit shifts to create bit array
    bits = [0] * N
    for i in range(N):
        bits[len(bits)-i-1] = (val >> i) % 2

    return bits


def inv_map(m):
    """ Create inverse mapping of ind array """
    out = [0] * len(m)
    for i in range(len(m)):
        out[int(m[i])] = int(i)

    return out


def grey_ordering(N):
    """ Generate grey order for arbitrary size PSK """

    # Initialize bits with just a 0 or 1
    out = [[0], [1]]

    # Calculate number of times to loop
    n = int(np.log2(N))

    # Make sure that N is a power of 2
    if 2 ** n != N:
        raise(Exception("N must be a power of 2"))

    # Loop through stages to generate binary-reflected grey code
    for k in range(n-1):
        nrows = len(out)
        # Append more rows of symbols
        for i in range(nrows):
            out.append(copy(out[nrows-i-1]))

        # Insert prefix to each row
        for i in range(nrows):
            out[i].insert(0, 0)
            out[i + nrows].insert(0, 1)
    return np.array(out)


def bit_ordering(N):
    """ Non-grey bit order """

    n = int(np.log2(N))
    if 2 ** n != N:
        raise(Exception("N must be a power of 2"))
    out = []
    for i in range(N):
        out.append([int(x) for x in ("{0:0%db}" % n).format(i)])
    return out


class PSK():
    """
    The PSK class generates and demodulates PSK symbols
    """

    def __init__(self, N=2, grey=False):
        """
        Initialize PSK class
        N is the PSK order (2 for bpsk, 4 for qpsk, ...)
        grey is a boolean indicating whether grey coding is used
        """

        # Calculate the number of bits
        n = int(np.log2(int(N)))

        # Make sure that N is a power of two
        self.N = int(N)
        if 2 ** n != self.N:
            raise(Exception("len(const_phases) should be a power of 2"))

        # Store whether grey coding is used
        self.grey = bool(grey)

        # Generate correct bit ordering
        if self.grey:
            self.bit_ordering = grey_ordering(self.N)
        else:
            self.bit_ordering = bit_ordering(self.N)

        # Generate list of indexes from grey code
        self.bit_ordering_inds = [bits_to_int(x) for x in self.bit_ordering]

        # Generate invese mapping
        self.to_grey = inv_map(self.bit_ordering_inds)

        # Generate constellation phases
        self.const_phases = np.array([x * 2 * np.pi / self.N
                                      for x in range(self.N)])

        # If not bpsk, then shift off of the axis
        if self.N != 2:
            self.const_phases += np.pi/self.N

    def gen(self, bits):
        """
        Generate psk symbols with N consetellation points
        const_phases should include the phase
        for each constellation at each index
        """

        N = len(self.const_phases)
        n = int(np.log2(N))

        # Get index of groups of n bits (1 bit  for bpsk,
        #                                2 bits for qpsk, ...)

        inds = [int(bits_to_int(bits[n * i:n * (i + 1)]))
                for i in range(int(len(bits)/n))]

        # If grey coding enabled change index

        if self.grey:
            inds = list(map(lambda x: self.to_grey[x], inds))

        phases = np.array([self.const_phases[i] for i in inds])

        symbols = np.exp(1j * phases)
        return symbols

    def slicer(self, syms):
        """
        A list of symbols generates a list of bits.
        """
        phases = np.angle(syms)
        if self.N != 2:
            phases -= np.pi/self.N

        inds = np.round(phases/(2*np.pi/self.N)) % self.N

        bits = [self.bit_ordering[int(ind)] for ind in inds]
        bits = [x for bit_vec in bits for x in bit_vec]
        return np.array(bits)


if __name__ == '__main__':

    parser = argparse_psk(
        "Encode or decode psk symbols",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--encode', '-e', action='store_true',
                       help="Encode a file to psk symbols")
    group.add_argument('--decode', '-d', action='store_true',
                       help="Decode psk symbols to a file")

    parser.add_argument('--order', '-N', type=int, default=4,
                        help="PSK Order (2 for bpsk, 4 for qpsk, ...)")
    parser.add_argument('--grey', '-g', action='store_true',
                        help="Use grey coding for PSK")
    parser.add_argument('--output', '-o',
                        help="Output filename default stdout")
    parser.add_argument('filename',
                        help="Input filename")

    args = vars(parser.parse_args())

    psk = PSK(args['order'], args['grey'])

    if args['output'] is None:
        fid_out = sys.stdout
    else:
        fid_out = open(args['output'], 'wb')

    fid_in = open(args['filename'], 'rb')

    if args['encode']:
        data = np.fromfile(fid_in, dtype='uint8')
        print(data)
        bits_vecvec = [int_to_bits(x, 8) for x in data]
        bits = [x for vec in bits_vecvec for x in vec]
        print(bits)
        syms = np.array(psk.gen(bits), dtype=np.complex64)
        syms.tofile(fid_out)
    else:
        data = np.fromfile(fid_in, dtype=np.complex64)
        bits = psk.slicer(data)
        bit_vecs = [bits[i*8:(i+1)*8] for i in range(int(len(bits)/8))]

        b = [bits_to_int(bit_vec) for bit_vec in bit_vecs]
        fid_out.write(bytes(b))
    fid_out.close()
