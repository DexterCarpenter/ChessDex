import sys
from models import bitboard
from gmpy2 import xmpz

TestBoard = bitboard.Board()

TestBoard.set_piece_bit("whitePawns", 8)
TestBoard.set_piece_bit("whitePawns", 9)
TestBoard.set_piece_bit("whitePawns", 63)
print(format(TestBoard.whitePawns, 'b'))


# a = xmpz(7)
# a[0] = 1
# print(bin(a))

# print(sys.getsizeof(a))


