from models.bitboard import (
    Board,
    Color,
    GameOutcome,
    Move,
    Piece,
)

INF = 10_000
MATE_SCORE = INF - 1

PIECE_VALUES = {
    Piece.PAWN: 1,
    Piece.KNIGHT: 3,
    Piece.BISHOP: 3,
    Piece.ROOK: 5,
    Piece.QUEEN: 9,
    Piece.KING: 0,
}


class Engine:
    """A class to represent the chess engine."""

    def __init__(self):
        pass

    def eval(self, board: Board) -> float:
        """Placeholder evaluation from White's perspective (centipawn-scale material).

        Positive scores favor White. Checkmate and draws are handled explicitly;
        replace this with a fuller evaluation later.
        """
        outcome = board.game_outcome()
        if outcome == GameOutcome.CHECKMATE:
            return -MATE_SCORE if board.whiteTurn else MATE_SCORE
        if outcome in (GameOutcome.STALEMATE, GameOutcome.THREEFOLD_REPETITION):
            return 0.0

        score = 0.0
        for color in Color:
            sign = 1 if color == Color.WHITE else -1
            for piece, value in PIECE_VALUES.items():
                if piece == Piece.KING:
                    continue
                bitboard = board.bitboards[(color, piece)]
                score += sign * value * int(bitboard).bit_count()
        return score

    def minimax(self, board: Board, depth: int) -> float:
        """Minimax search to the given depth, scoring leaves with eval().

        Returns the best achievable score from White's perspective.
        """
        if board.is_game_over() or depth == 0:
            return self.eval(board)

        if board.whiteTurn:
            best = -INF
            for move in board.get_all_legal_moves():
                board.make_move(move)
                value = self.minimax(board, depth - 1)
                board.undo_move()
                if value > best:
                    best = value
            return best

        best = INF
        for move in board.get_all_legal_moves():
            board.make_move(move)
            value = self.minimax(board, depth - 1)
            board.undo_move()
            if value < best:
                best = value
        return best

    def get_best_move(self, board: Board, depth: int) -> Move | None:
        """Return the best legal move for the side to move at the given search depth.

        Uses minimax() to score each root move. Returns None when there are no
        legal moves (checkmate or stalemate).
        """
        legal_moves = board.get_all_legal_moves()
        if not legal_moves:
            return None

        if board.whiteTurn:
            best_value = -INF
            best_move = legal_moves[0]
            for move in legal_moves:
                board.make_move(move)
                value = self.minimax(board, depth - 1)
                board.undo_move()
                if value > best_value:
                    best_value = value
                    best_move = move
            return best_move

        best_value = INF
        best_move = legal_moves[0]
        for move in legal_moves:
            board.make_move(move)
            value = self.minimax(board, depth - 1)
            board.undo_move()
            if value < best_value:
                best_value = value
                best_move = move
        return best_move