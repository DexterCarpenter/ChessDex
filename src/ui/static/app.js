/**
 * ChessDex play UI — talks to /api/* (same contract a future web app could use).
 */

const SESSION_KEY = "chessdex_session_id";
const SESSION_HEADER = "X-Session-Id";

const PIECE_TYPE_NAMES = {
  king: "King",
  queen: "Queen",
  rook: "Rook",
  bishop: "Bishop",
  knight: "Knight",
  pawn: "Pawn",
};

const boardEl = document.getElementById("board");
const statusEl = document.getElementById("status");
const moveListEl = document.getElementById("move-list");
const promoBar = document.getElementById("promo-bar");
const btnStep = document.getElementById("btn-step");
const autoWrap = document.getElementById("auto-wrap");
const autoPlay = document.getElementById("auto-play");

let state = null;
let selectedSq = null;
let pendingPromo = null;
let autoTimer = null;

function getSessionId() {
  let id = localStorage.getItem(SESSION_KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

function pieceAssetUrl(piece) {
  const color = piece.color === "white" ? "White" : "Black";
  const type = PIECE_TYPE_NAMES[piece.type];
  return `/assets/${color}${type}.svg`;
}

async function api(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    [SESSION_HEADER]: getSessionId(),
    ...options.headers,
  };
  const res = await fetch(path, { ...options, headers });
  const text = await res.text();
  if (!text) {
    throw new Error(
      res.ok
        ? "Server returned no response"
        : `Server error (${res.status}) — try again or lower engine depth`
    );
  }
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    const preview = text.slice(0, 200);
    throw new Error(
      res.ok
        ? "Invalid JSON from server"
        : `Server error (${res.status}): ${preview}`
    );
  }
  if (!res.ok && !data.state) {
    throw new Error(data.error || res.statusText);
  }
  return data;
}

function currentMode() {
  return document.querySelector('input[name="mode"]:checked')?.value;
}

async function refreshEngineHint() {
  if (!state?.show_engine_hint) return;
  try {
    const data = await api("/api/state");
    state.engine_hint = data.engine_hint;
    renderBoard();
    renderStatus();
  } catch {
    /* hint refresh is best-effort */
  }
}

function applyState(s, { refreshHint = false } = {}) {
  state = s;
  renderBoard();
  renderStatus();
  renderHistory();
  syncControls();
  maybeAutoEngine();
  if (refreshHint) {
    refreshEngineHint();
  }
}

function syncControls() {
  document.getElementById("show-hint").checked = !!state.show_engine_hint;
  document.getElementById("depth").value = state.engine_depth;
  document.getElementById("depth-val").textContent = String(state.engine_depth);
  const modeInput = document.querySelector(
    `input[name="mode"][value="${state.mode}"]`
  );
  if (modeInput) modeInput.checked = true;

  const engineMode = state.mode === "engine_engine";
  btnStep.classList.toggle("hidden", !engineMode);
  autoWrap.classList.toggle("hidden", !engineMode);
}

function renderStatus() {
  let text = `${state.side_to_move} to move`;
  if (state.in_check) text += " (check)";
  if (state.status) {
    text = state.status;
    statusEl.classList.add("game-over");
  } else {
    statusEl.classList.remove("game-over");
  }
  if (!state.can_human_move && state.mode !== "engine_engine" && !state.status) {
    text += " — engine thinking…";
  }
  if (state.engine_hint && state.show_engine_hint) {
    text += ` · hint: ${state.engine_hint.san}`;
  }
  statusEl.textContent = text;
}

function renderHistory() {
  moveListEl.innerHTML = "";
  (state.move_history || []).forEach((san) => {
    const li = document.createElement("li");
    li.textContent = san;
    moveListEl.appendChild(li);
  });
}

function squareClasses(sq) {
  const classes = ["square", sq.light ? "light" : "dark"];
  const alg = sq.sq;

  if (selectedSq === alg) classes.push("selected");
  if (pendingPromo && pendingPromo.from === alg) classes.push("selected");

  if (state.last_move) {
    if (state.last_move.from === alg || state.last_move.to === alg) {
      classes.push(state.last_move.from === alg ? "last-from" : "last-to");
    }
  }

  if (state.engine_hint && state.show_engine_hint) {
    if (state.engine_hint.from === alg) classes.push("hint-from");
    if (state.engine_hint.to === alg) classes.push("hint-to");
  }

  return classes;
}

function renderBoard() {
  boardEl.innerHTML = "";
  boardEl.classList.toggle("flipped", !!state.flip_board);

  const squares = state.flip_board ? [...state.squares].reverse() : state.squares;

  squares.forEach((sq) => {
    const el = document.createElement("button");
    el.type = "button";
    el.className = squareClasses(sq).join(" ");
    el.dataset.sq = sq.sq;
    if (sq.piece) {
      const img = document.createElement("img");
      img.className = "piece-img";
      img.src = pieceAssetUrl(sq.piece);
      img.alt = `${sq.piece.color} ${sq.piece.type}`;
      el.appendChild(img);
      el.classList.add("has-piece");
      el.setAttribute(
        "aria-label",
        `${sq.piece.color} ${sq.piece.type} on ${sq.sq}`
      );
    } else {
      el.setAttribute("aria-label", sq.sq);
    }
    if (!state.can_human_move || state.status) {
      el.disabled = true;
    }
    el.addEventListener("click", () => onSquareClick(sq.sq));
    boardEl.appendChild(el);
  });

  if (selectedSq && state.can_human_move) {
    highlightLegalTargets(selectedSq);
  }
}

async function highlightLegalTargets(from) {
  try {
    const { moves } = await api(
      `/api/legal_moves?sq=${encodeURIComponent(from)}`
    );
    const targets = new Set(moves.map((m) => m.to));
    boardEl.querySelectorAll(".square").forEach((el) => {
      if (targets.has(el.dataset.sq)) {
        el.classList.add("legal-target");
      }
    });
  } catch (err) {
    statusEl.textContent = err.message;
  }
}

async function onSquareClick(alg) {
  if (!state.can_human_move || pendingPromo) return;

  if (!selectedSq) {
    const sq = state.squares.find((s) => s.sq === alg);
    if (!sq?.piece) return;
    const humanColor = state.mode === "human_black" ? "black" : "white";
    if (state.mode !== "human_human" && sq.piece.color !== humanColor) return;
    if (state.mode === "human_human" && sq.piece.color !== state.side_to_move)
      return;
    selectedSq = alg;
    renderBoard();
    return;
  }

  if (selectedSq === alg) {
    selectedSq = null;
    renderBoard();
    return;
  }

  await submitMove(selectedSq, alg);
}

async function submitMove(from, to, promotion) {
  try {
    const body = { from, to };
    if (promotion) body.promotion = promotion;
    const data = await api("/api/move", {
      method: "POST",
      body: JSON.stringify(body),
    });

    if (data.needs_promotion) {
      pendingPromo = { from, to };
      promoBar.classList.remove("hidden");
      selectedSq = null;
      renderBoard();
      return;
    }

    pendingPromo = null;
    promoBar.classList.add("hidden");
    selectedSq = null;
    if (data.state) applyState(data.state, { refreshHint: true });
  } catch (err) {
    statusEl.textContent = err.message;
    selectedSq = null;
    renderBoard();
  }
}

function maybeAutoEngine() {
  clearTimeout(autoTimer);
  if (
    state.mode === "engine_engine" &&
    autoPlay.checked &&
    state.is_engine_turn &&
    !state.status
  ) {
    autoTimer = setTimeout(engineStep, 450);
  }
}

async function engineStep() {
  try {
    const data = await api("/api/engine_step", { method: "POST", body: "{}" });
    if (data.state) applyState(data.state, { refreshHint: true });
  } catch (err) {
    statusEl.textContent = err.message;
  }
}

async function loadState() {
  const data = await api("/api/state");
  applyState(data);
}

async function newGame() {
  const data = await api("/api/new", {
    method: "POST",
    body: JSON.stringify({
      mode: currentMode(),
      engine_depth: Number(document.getElementById("depth").value),
      show_engine_hint: document.getElementById("show-hint").checked,
    }),
  });
  applyState(data, { refreshHint: true });
  selectedSq = null;
  pendingPromo = null;
  promoBar.classList.add("hidden");
}

async function updateConfig(patch) {
  const data = await api("/api/config", {
    method: "POST",
    body: JSON.stringify(patch),
  });
  applyState(data, { refreshHint: true });
}

document.getElementById("btn-new").addEventListener("click", newGame);
document.getElementById("btn-undo").addEventListener("click", async () => {
  const data = await api("/api/undo", { method: "POST", body: "{}" });
  if (data.state) applyState(data.state, { refreshHint: true });
  selectedSq = null;
});
btnStep.addEventListener("click", engineStep);

document.getElementById("show-hint").addEventListener("change", (e) => {
  updateConfig({ show_engine_hint: e.target.checked });
});

document.getElementById("depth").addEventListener("input", (e) => {
  document.getElementById("depth-val").textContent = e.target.value;
});
document.getElementById("depth").addEventListener("change", (e) => {
  updateConfig({ engine_depth: Number(e.target.value) });
});

document.querySelectorAll('input[name="mode"]').forEach((el) => {
  el.addEventListener("change", newGame);
});

promoBar.querySelectorAll("[data-promo]").forEach((btn) => {
  btn.addEventListener("click", () => {
    if (!pendingPromo) return;
    submitMove(pendingPromo.from, pendingPromo.to, btn.dataset.promo);
    promoBar.classList.add("hidden");
  });
});
document.getElementById("promo-cancel").addEventListener("click", () => {
  pendingPromo = null;
  promoBar.classList.add("hidden");
  selectedSq = null;
  renderBoard();
});

loadState().catch((err) => {
  statusEl.textContent = `Cannot reach server: ${err.message}`;
});
