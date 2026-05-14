from models import bitboard
from gmpy2 import mpz

TestBoard = bitboard.Board()

print(TestBoard.position)

a = mpz(7)
bin(a)
a = a.setbit(48)
bin(a)


