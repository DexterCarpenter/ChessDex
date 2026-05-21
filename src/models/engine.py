import threading

from models.bitboard import (
    Board,
    Color,
    Move,
    Piece,
)

_engine_search_lock = threading.Lock()

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

    def _material_eval(self, board: Board) -> float:
        """Material balance from White's perspective (no terminal or draw logic)."""
        score = 0.0
        for color in Color:
            sign = 1 if color == Color.WHITE else -1
            for piece, value in PIECE_VALUES.items():
                if piece == Piece.KING:
                    continue
                bitboard = board.bitboards[(color, piece)]
                score += sign * value * int(bitboard).bit_count()
        return score

    def _terminal_eval(self, board: Board) -> float:
        """Score when the side to move has no legal moves (checkmate or stalemate)."""
        color = Color.WHITE if board.whiteTurn else Color.BLACK
        if board._is_in_check(color):
            return -MATE_SCORE if board.whiteTurn else MATE_SCORE
        return 0.0

    def eval(self, board: Board) -> float:
        """Placeholder evaluation from White's perspective (centipawn-scale material).

        Positive scores favor White. Checkmate, stalemate, and threefold repetition
        are handled explicitly; replace material scoring with a fuller eval later.
        """
        legal_moves = board.get_all_legal_moves()
        if not legal_moves:
            return self._terminal_eval(board)
        if board._repetition_count() >= 3:
            return 0.0
        return self._material_eval(board)

    def minimax(self, board: Board, depth: int) -> float:
        """Minimax search to the given depth, scoring leaves with eval().

        Returns the best achievable score from White's perspective.
        """
        if depth <= 0:
            return self._material_eval(board)

        legal_moves = board.get_all_legal_moves()
        if not legal_moves:
            return self._terminal_eval(board)

        if board.whiteTurn:
            best = -INF
            for move in legal_moves:
                board.make_move(move)
                value = self.minimax(board, depth - 1)
                board.undo_move()
                if value > best:
                    best = value
            return best

        best = INF
        for move in legal_moves:
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
        with _engine_search_lock:
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
