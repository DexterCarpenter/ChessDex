import sys
from models import bitboard
from gmpy2 import xmpz

TestBoard = bitboard.Board()

# print(TestBoard.position)

a = xmpz(7)
a[0] = 1
print(bin(a))

print(sys.getsizeof(a))


