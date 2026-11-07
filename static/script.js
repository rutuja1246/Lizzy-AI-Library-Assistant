const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const themeButton = document.getElementById("theme-toggle");

// ============================
// DARK MODE
// ============================

function applyTheme(theme) {
  document.body.classList.toggle("dark", theme === "dark");
  themeButton.textContent = theme === "dark" ? "☀️" : "🌙";
}

const savedTheme = localStorage.getItem("theme") || "light";
applyTheme(savedTheme);

themeButton.addEventListener("click", () => {
  const newTheme = document.body.classList.contains("dark") ? "light" : "dark";

  localStorage.setItem("theme", newTheme);
  applyTheme(newTheme);
});

// ============================
// SEND MESSAGE
// ============================

sendBtn.addEventListener("click", sendMessage);

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    sendMessage();
  }
});

async function sendMessage() {
  const text = input.value.trim();

  if (!text) return;

  // Display user message
  addMessage(text, "user");

  input.value = "";

  sendBtn.disabled = true;

  // Show typing indicator
  const typing = showTyping();

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: text,
      }),
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const data = await response.json();

    typing.remove();

    addMessage(data.response || "I couldn't generate a response.", "bot");
  } catch (error) {
    console.error("Chat error:", error);

    typing.remove();

    addMessage(
      "Sorry! I'm having trouble connecting to the server. Please try again.",
      "bot",
    );
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

// ============================
// ADD MESSAGE
// ============================

function addMessage(text, sender) {
  const message = document.createElement("div");
  message.className = `message ${sender}`;

  const name = document.createElement("div");
  name.className = "sender";
  name.textContent = sender === "bot" ? "📚 Lizzy" : "You";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  message.appendChild(name);
  message.appendChild(bubble);

  chatBox.appendChild(message);

  scrollToBottom();
}

// ============================
// TYPING INDICATOR
// ============================

function showTyping() {
  const typing = document.createElement("div");
  typing.className = "message bot";

  typing.id = "typing";

  const name = document.createElement("div");
  name.className = "sender";
  name.textContent = "📚 Lizzy";

  const bubble = document.createElement("div");
  bubble.className = "bubble typing";
  bubble.textContent = "Lizzy is thinking...";

  typing.appendChild(name);
  typing.appendChild(bubble);

  chatBox.appendChild(typing);

  scrollToBottom();

  return typing;
}

// ============================
// AUTO SCROLL
// ============================

function scrollToBottom() {
  chatBox.scrollTop = chatBox.scrollHeight;
}
