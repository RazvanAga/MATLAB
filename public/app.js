// Frontend: open an EventSource per message and render the agentic timeline.
// Events (see backend/events.py): agent_text, tool_use, tool_result, error, done.

const timeline = document.getElementById("timeline");
const emptyState = document.getElementById("empty-state");
const composer = document.getElementById("composer");
const input = document.getElementById("message");
const sendBtn = document.getElementById("send");
const modelSelect = document.getElementById("model");

// Map of tool_use id -> card element, so tool_result fills the right card.
const cards = new Map();
let source = null;

function clearEmptyState() {
  if (emptyState && emptyState.parentNode) emptyState.remove();
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
