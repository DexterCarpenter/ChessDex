import sys
from models.bitboard import Board, ChessPiece, Color, Piece
from utils import *

TestBoard = Board()

TestBoard.setup_starting_position()

print(TestBoard.render())

