const state = {
  sessionId: localStorage.getItem("jarvis.sessionId") || "",
  status: null,
  sending: false,
};

const elements = {
  chatForm: document.querySelector("#chatForm"),
  clearSession: document.querySelector("#clearSession"),
  loadSession: document.querySelector("#loadSession"),
  memoryValue: document.querySelector("#memoryValue"),
  messageInput: document.querySelector("#messageInput"),
  messages: document.querySelector("#messages"),
  modelLabel: document.querySelector("#modelLabel"),
  newSession: document.querySelector("#newSession"),
  providerValue: document.querySelector("#providerValue"),
  refreshSessions: document.querySelector("#refreshSessions"),
  sendButton: document.querySelector("#sendButton"),
  sessionInput: document.querySelector("#sessionInput"),
  sessionList: document.querySelector("#sessionList"),
};

async function requestJson(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "Request failed.");
  }
  return payload;
}

function setSessionId(sessionId) {
  state.sessionId = sessionId;
  localStorage.setItem("jarvis.sessionId", sessionId);
  elements.sessionInput.value = sessionId;
}

function renderMessages(messages) {
  elements.messages.innerHTML = "";
  if (!messages.length) {
    appendMessage("assistant", "J.A.R.V.I.S. online. Awaiting instruction.");
    return;
  }
  messages.forEach((message) => appendMessage(message.role, message.content));
}

function appendMessage(role, content) {
  const item = document.createElement("article");
  item.className = `message ${role}`;

  const label = document.createElement("div");
  label.className = "message-role";
  label.textContent = role === "user" ? "You" : role;

  const body = document.createElement("div");
  body.textContent = content;

  item.append(label, body);
  elements.messages.append(item);
  elements.messages.scrollTop = elements.messages.scrollHeight;
}

function renderSessions(sessions) {
  elements.sessionList.innerHTML = "";
  sessions.forEach((session) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `session-item ${session.id === state.sessionId ? "active" : ""}`;

    const id = document.createElement("span");
    id.className = "session-id";
    id.textContent = session.id;

    const meta = document.createElement("span");
    meta.className = "session-meta";
    meta.textContent = `${session.message_count} messages`;

    button.append(id, meta);
    button.addEventListener("click", () => loadSession(session.id));
    elements.sessionList.append(button);
  });
}

async function loadStatus() {
  const status = await requestJson("/api/status");
  state.status = status;

  if (!state.sessionId) {
    setSessionId(status.default_session_id);
  } else {
    elements.sessionInput.value = state.sessionId;
  }

  elements.modelLabel.textContent = status.model;
  elements.providerValue.textContent = status.provider;
  elements.memoryValue.textContent = status.memory_db_path;
}

async function loadHistory() {
  const payload = await requestJson("/api/history", {
    method: "POST",
    body: JSON.stringify({ session_id: state.sessionId }),
  });
  renderMessages(payload.messages);
}

async function loadSessions() {
  const payload = await requestJson("/api/sessions");
  renderSessions(payload.sessions);
}

async function loadSession(sessionId) {
  setSessionId(sessionId);
  await loadHistory();
  await loadSessions();
}

async function sendMessage(message) {
  appendMessage("user", message);
  state.sending = true;
  elements.sendButton.disabled = true;
  elements.sendButton.textContent = "Wait";

  try {
    const payload = await requestJson("/api/message", {
      method: "POST",
      body: JSON.stringify({ session_id: state.sessionId, message }),
    });
    setSessionId(payload.session_id);
    renderMessages(payload.messages);
    await loadSessions();
  } catch (error) {
    appendMessage("error", error.message);
  } finally {
    state.sending = false;
    elements.sendButton.disabled = false;
    elements.sendButton.textContent = "Send";
  }
}

elements.chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = elements.messageInput.value.trim();
  if (!message || state.sending) {
    return;
  }
  elements.messageInput.value = "";
  await sendMessage(message);
});

elements.messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    elements.chatForm.requestSubmit();
  }
});

elements.loadSession.addEventListener("click", async () => {
  const sessionId = elements.sessionInput.value.trim();
  if (sessionId) {
    await loadSession(sessionId);
  }
});

elements.newSession.addEventListener("click", async () => {
  const sessionId = crypto.randomUUID();
  await loadSession(sessionId);
});

elements.refreshSessions.addEventListener("click", loadSessions);

elements.clearSession.addEventListener("click", async () => {
  const payload = await requestJson("/api/clear", {
    method: "POST",
    body: JSON.stringify({ session_id: state.sessionId }),
  });
  renderMessages(payload.messages);
  await loadSessions();
});

async function boot() {
  try {
    await loadStatus();
    await loadHistory();
    await loadSessions();
  } catch (error) {
    appendMessage("error", error.message);
  }
}

boot();

