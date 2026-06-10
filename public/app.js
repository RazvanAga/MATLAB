// Frontend: open an EventSource per message and render the agentic timeline.
// Events (see backend/events.py): agent_text, tool_use, tool_result, error, done.

// Scripted demo prompts (Issue 04). High-level on purpose — the system prompt
// (backend/agent.py) handles figure export, check-before-run, the read-only
// Simulink guardrail, defensive workspace re-derivation, and the no-Control-
// System-Toolbox constraint, so these stay focused on the engineering task.
// 1 + 2 share one mass-spring-damper response; 3 is the same physics in Simulink.
const PROMPTS = {
  // 1 — mass-spring-damper step response in MATLAB (underdamped → clear overshoot).
  "1":
    "Simulate the step response of a mass-spring-damper system in MATLAB. " +
    "Use mass m = 1 kg, damping coefficient c = 2 N·s/m, and stiffness " +
    "k = 20 N/m, with a unit step force applied at t = 0. Solve for the " +
    "displacement over 0 to 5 seconds, then plot displacement versus time " +
    "with labeled axes and a title.",
  // 2 — overshoot/settling follow-up; reuses step 1's response, computed by hand.
  "2":
    "From that same step response, compute the percent overshoot relative to " +
    "the steady-state value and the 2% settling time. Calculate both directly " +
    "from the displacement array. Print the two values, then redraw the plot " +
    "with the peak and the settling time marked.",
  // 3 — same system as a Simulink block diagram: read-only inspect + simulate.
  "3":
    "Open the Simulink model mbd_demo.slx — the same mass-spring-damper as a " +
    "block diagram. Give a short overview of its structure, then simulate it " +
    "and read the logged displacement signal. Plot that signal and confirm it " +
    "matches the MATLAB response from step 1 (same physics, now in Simulink).",
  // extra-safe — bulletproof, no workspace/Simulink dependency, always yields a figure.
  "extra":
    "In MATLAB, create a time vector t from 0 to 2*pi and plot sin(t) and " +
    "cos(t) together on the same axes. Add a legend, a grid, axis labels, and " +
    "a title.",
};
const RESET_PROMPT = "Run the following MATLAB command exactly: close all; clear";

const EMPTY_STATE_HTML = `
  <h2 class="empty-title">MATLAB&nbsp;/&nbsp;Simulink MCP Demo</h2>
  <p class="empty-context">chatbot care conduce MATLAB/Simulink live prin MCP</p>
  <p class="empty-hint">Select a numbered step above to start, or type a custom message below.</p>
`;

const timeline = document.getElementById("timeline");
const composer = document.getElementById("composer");
const input = document.getElementById("message");
const sendBtn = document.getElementById("send");
const modelSelect = document.getElementById("model");
const promptBtns = document.querySelectorAll(".prompt-btn");
const resetBtn = document.getElementById("reset-btn");

// Map of tool_use id -> card element, so tool_result fills the right card.
const cards = new Map();
let source = null;

function clearEmptyState() {
  const el = document.getElementById("empty-state");
  if (el) el.remove();
}

function restoreEmptyState() {
  while (timeline.firstChild) timeline.removeChild(timeline.firstChild);
  const el = document.createElement("div");
  el.id = "empty-state";
  el.className = "empty-state";
  el.innerHTML = EMPTY_STATE_HTML;
  timeline.appendChild(el);
}

function scrollToEnd() {
  timeline.scrollTop = timeline.scrollHeight;
}

function renderAgentText(text) {
  clearEmptyState();
  const el = document.createElement("div");
  el.className = "agent-text";
  el.innerHTML = marked.parse(text);
  timeline.appendChild(el);
  scrollToEnd();
}

function renderToolUse({ id, name, input }) {
  clearEmptyState();
  const card = document.createElement("div");
  card.className = "tool-card running";

  const head = document.createElement("div");
  head.className = "tool-head";
  head.innerHTML = `<span>🔧</span><span class="tool-name">${escapeHtml(name)}</span>`;
  const spinner = document.createElement("div");
  spinner.className = "spinner";
  head.appendChild(spinner);

  const pre = document.createElement("pre");
  const code = document.createElement("code");
  code.className = "language-matlab";
  code.textContent = formatInput(input);
  pre.appendChild(code);

  const result = document.createElement("div");
  result.className = "tool-result";
  result.textContent = "running in MATLAB…";

  card.append(head, pre, result);
  timeline.appendChild(card);
  cards.set(id, card);
  if (window.hljs) hljs.highlightElement(code);
  scrollToEnd();
}

function renderToolResult({ id, output, is_error }) {
  const card = cards.get(id);
  if (!card) return;
  card.classList.remove("running");
  const spinner = card.querySelector(".spinner");
  if (spinner) spinner.remove();
  const result = card.querySelector(".tool-result");
  result.textContent = output || "(no output)";
  if (is_error) result.style.color = "var(--error)";
  scrollToEnd();
}

function renderFigure({ id, name, mime, data }) {
  const src = `data:${mime};base64,${data}`;
  const img = document.createElement("img");
  img.className = "tool-figure";
  img.src = src;
  img.alt = name || "MATLAB figure";
  img.title = "Click to enlarge";
  img.addEventListener("click", () => openLightbox(src, img.alt));

  // Attach to the card that produced it; fall back to the timeline.
  const card = cards.get(id);
  (card || timeline).appendChild(img);
  scrollToEnd();
}

function openLightbox(src, alt) {
  const overlay = document.getElementById("lightbox");
  const img = document.getElementById("lightbox-img");
  img.src = src;
  img.alt = alt || "";
  overlay.classList.add("open");
}

function closeLightbox() {
  const overlay = document.getElementById("lightbox");
  overlay.classList.remove("open");
  document.getElementById("lightbox-img").src = "";
}

function renderError({ message, traceback }) {
  clearEmptyState();
  const card = document.createElement("div");
  card.className = "error-card";
  const msg = document.createElement("div");
  msg.className = "error-msg";
  msg.textContent = message;
  card.appendChild(msg);
  if (traceback) {
    const details = document.createElement("details");
    const summary = document.createElement("summary");
    summary.textContent = "Show traceback";
    const pre = document.createElement("pre");
    pre.textContent = traceback;
    details.append(summary, pre);
    card.appendChild(details);
  }
  timeline.appendChild(card);
  scrollToEnd();
}

function formatInput(input) {
  if (typeof input === "string") return input;
  try {
    return JSON.stringify(input, null, 2);
  } catch {
    return String(input);
  }
}

function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}

function setBusy(busy) {
  input.disabled = busy;
  sendBtn.disabled = busy;
  modelSelect.disabled = busy;
  promptBtns.forEach((b) => { b.disabled = busy; });
  resetBtn.disabled = busy;
  if (!busy) input.focus();
}

function startTurn(message) {
  setBusy(true);
  cards.clear();
  const params = new URLSearchParams({ message, model: modelSelect.value });
  source = new EventSource("/api/stream?" + params.toString());

  source.onmessage = (e) => {
    const event = JSON.parse(e.data);
    switch (event.type) {
      case "agent_text": renderAgentText(event.text); break;
      case "tool_use": renderToolUse(event); break;
      case "tool_result": renderToolResult(event); break;
      case "figure": renderFigure(event); break;
      case "error": renderError(event); break;
      case "done": closeTurn(); break;
    }
  };

  source.onerror = () => {
    // Network drop or server close without a `done` — fail gracefully.
    renderError({ message: "Connection to the server was lost.", traceback: "" });
    closeTurn();
  };
}

function closeTurn() {
  if (source) {
    source.close();
    source = null;
  }
  setBusy(false);
}

composer.addEventListener("submit", (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message || source) return;
  input.value = "";
  startTurn(message);
});

promptBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    const prompt = PROMPTS[btn.dataset.step];
    if (!prompt || source) return;
    startTurn(prompt);
  });
});

resetBtn.addEventListener("click", () => {
  if (source) return;
  restoreEmptyState();
  startTurn(RESET_PROMPT);
});

// Lightbox: click the backdrop or press Escape to close.
document.getElementById("lightbox").addEventListener("click", closeLightbox);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeLightbox();
});
