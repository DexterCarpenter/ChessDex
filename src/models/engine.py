import random
import threading
from enum import Enum, auto

from models.bitboard import (
    MATERIAL_BY_PIECE,
    Board,
    Color,
    Move,
    Piece,
)

_engine_search_lock = threading.Lock()

INF = 10_000
MATE_SCORE = INF - 1

PIECE_VALUES = MATERIAL_BY_PIECE

# MVV-LVA: victim value * 10 - attacker value (higher searched first)
_MVV_LVA_VICTIM = {
    None: 0,
    Piece.PAWN: 1,
    Piece.KNIGHT: 3,
    Piece.BISHOP: 3,
    Piece.ROOK: 5,
    Piece.QUEEN: 9,
    Piece.KING: 0,
}


class _TTFlag(Enum):
    EXACT = auto()
    LOWER = auto()
    UPPER = auto()


class Engine:
    """Chess engine with alpha-beta search, move ordering, and transposition table."""

    def __init__(self) -> None:
        self._tt: dict[int, tuple[int, float, _TTFlag]] = {}
        self._killer_moves: list[list[Move | None]] = [
            [None, None] for _ in range(64)
        ]

    def _material_eval(self, board: Board) -> float:
        """Material balance from White's perspective (O(1) incremental)."""
        return board.material_score

    def _terminal_eval(self, board: Board, color: Color) -> float:
        """Score when color has no legal moves (checkmate or stalemate)."""
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
            color = Color.WHITE if board.whiteTurn else Color.BLACK
            return self._terminal_eval(board, color)
        if board._repetition_count() >= 3:
            return 0.0
        return self._material_eval(board)

    def _zobrist_key(self, board: Board) -> int:
        return board.zobrist_hash

    def _attacker_piece(self, board: Board, move: Move) -> Piece | None:
        piece = board.get_piece_at(move.from_square)
        return piece.name if piece is not None else None

    def _victim_piece(self, board: Board, move: Move) -> Piece | None:
        captured = board.get_piece_at(move.to_square)
        if captured is not None and captured.color != (
            Color.WHITE if board.whiteTurn else Color.BLACK
        ):
            return captured.name
        ep = board._en_passant_target_index(
            Color.WHITE if board.whiteTurn else Color.BLACK
        )
        if ep is not None and ep == move.to_square.idx:
            return Piece.PAWN
        return None

    def _move_score(self, board: Board, move: Move, depth: int) -> int:
        victim = self._victim_piece(board, move)
        if victim is not None:
            attacker = self._attacker_piece(board, move)
            return _MVV_LVA_VICTIM[victim] * 10 - PIECE_VALUES.get(attacker or Piece.PAWN, 0)
        if depth < len(self._killer_moves):
            for killer in self._killer_moves[depth]:
                if killer is not None and (
                    killer.from_square.idx == move.from_square.idx
                    and killer.to_square.idx == move.to_square.idx
                ):
                    return 1
        return 0

    def _order_moves(self, board: Board, moves: list[Move], depth: int) -> list[Move]:
        return sorted(
            moves,
            key=lambda m: self._move_score(board, m, depth),
            reverse=True,
        )

    def _alphabeta(
        self,
        board: Board,
        depth: int,
        alpha: float,
        beta: float,
        ply: int = 0,
    ) -> float:
        """Alpha-beta search; returns score from White's perspective."""
        if depth <= 0:
            return self._material_eval(board)

        key = self._zobrist_key(board)
        tt_entry = self._tt.get(key)
        if tt_entry is not None:
            tt_depth, tt_score, tt_flag = tt_entry
            if tt_depth >= depth:
                if tt_flag == _TTFlag.EXACT:
                    return tt_score
                if tt_flag == _TTFlag.LOWER:
                    alpha = max(alpha, tt_score)
                elif tt_flag == _TTFlag.UPPER:
                    beta = min(beta, tt_score)
                if alpha >= beta:
                    return tt_score

        legal_moves = board.get_all_legal_moves()
        if not legal_moves:
            color = Color.WHITE if board.whiteTurn else Color.BLACK
            return self._terminal_eval(board, color)

        maximizing = board.whiteTurn
        ordered = self._order_moves(board, legal_moves, ply)
        orig_alpha = alpha
        best_score = -INF if maximizing else INF

        for move in ordered:
            board.make_move(move)
            value = self._alphabeta(board, depth - 1, alpha, beta, ply + 1)
            board.undo_move()

            if maximizing:
                if value > best_score:
                    best_score = value
                alpha = max(alpha, value)
            else:
                if value < best_score:
                    best_score = value
                beta = min(beta, value)

            if beta <= alpha:
                if self._victim_piece(board, move) is None and ply < len(
                    self._killer_moves
                ):
                    killers = self._killer_moves[ply]
                    if killers[0] != move:
                        killers[1] = killers[0]
                        killers[0] = move
                break

        if best_score <= orig_alpha:
            flag = _TTFlag.UPPER
        elif best_score >= beta:
            flag = _TTFlag.LOWER
        else:
            flag = _TTFlag.EXACT
        self._tt[key] = (depth, best_score, flag)
        return best_score

    def minimax(self, board: Board, depth: int) -> float:
        """Minimax search (alpha-beta under the hood) from White's perspective."""
        return self._alphabeta(board, depth, -INF, INF)

    def get_best_move(self, board: Board, depth: int) -> Move | None:
        """Return the best legal move via iterative deepening alpha-beta search."""
        with _engine_search_lock:
            legal_moves = board.get_all_legal_moves()
            if not legal_moves:
                return None

            self._tt.clear()
            for row in self._killer_moves:
                row[0] = None
                row[1] = None

            best_moves: list[Move] = []
            maximizing = board.whiteTurn

            for current_depth in range(1, depth + 1):
                ordered = self._order_moves(board, legal_moves, 0)
                best_value = -INF if maximizing else INF
                depth_best: list[Move] = []

                for move in ordered:
                    board.make_move(move)
                    value = self._alphabeta(
                        board,
                        current_depth - 1,
                        -INF,
                        INF,
                        ply=1,
                    )
                    board.undo_move()

                    if maximizing:
                        if value > best_value:
                            best_value = value
                            depth_best = [move]
                        elif value == best_value:
                            depth_best.append(move)
                    elif value < best_value:
                        best_value = value
                        depth_best = [move]
                    elif value == best_value:
                        depth_best.append(move)

                if depth_best:
                    best_moves = depth_best

            if not best_moves:
                return random.choice(legal_moves)
            return random.choice(best_moves)
