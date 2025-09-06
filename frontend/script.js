// ==============================
// TalksyAI Frontend Script
// Handles Login, Register, Logout, Theme Toggle, and Chat
// ==============================

const API_BASE = "http://127.0.0.1:8787/api";

// ------------------------------
// THEME TOGGLE
// ------------------------------
const themeToggleBtn = document.getElementById("theme-toggle");
const htmlEl = document.documentElement;

// Load saved theme
if(localStorage.getItem("theme") === "light") {
  htmlEl.classList.add("light");
}

if(themeToggleBtn) {
  themeToggleBtn.addEventListener("click", () => {
    htmlEl.classList.toggle("light");
    const theme = htmlEl.classList.contains("light") ? "light" : "dark";
    localStorage.setItem("theme", theme);
  });
}

// ------------------------------
// LOGIN
// ------------------------------
const loginBtn = document.getElementById("login-btn");
if(loginBtn) {
  loginBtn.addEventListener("click", async () => {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    if(!username || !password) {
      alert("Please enter username and password");
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/login`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ username, password })
      });

      const data = await res.json();
      if(res.ok) {
        localStorage.setItem("token", data.access_token);
        window.location = "home.html"; // Redirect to home after login
      } else {
        alert(data.detail || "Login failed");
      }
    } catch(err) {
      console.error(err);
      alert("Login failed. Please try again.");
    }
  });
}

// ------------------------------
// REGISTER
// ------------------------------
const registerBtn = document.getElementById("register-btn");
if(registerBtn) {
  registerBtn.addEventListener("click", async () => {
    const username = document.getElementById("reg-username").value.trim();
    const password = document.getElementById("reg-password").value;

    if(!username || !password) {
      alert("Please enter username and password");
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/register`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ username, password })
      });

      const data = await res.json();
      if(res.ok) {
        alert("Registration successful! Please login.");
        window.location = "index.html"; // Go to login page
      } else {
        alert(data.detail || "Registration failed");
      }
    } catch(err) {
      console.error(err);
      alert("Registration failed. Please try again.");
    }
  });
}

// ------------------------------
// LOGOUT
// ------------------------------
const logoutBtn = document.getElementById("logout-btn");
if(logoutBtn) {
  logoutBtn.addEventListener("click", () => {
    localStorage.removeItem("token");
    alert("✅ Logged out!");
    window.location = "index.html";
  });
}

// ------------------------------
// REDIRECT IF NOT LOGGED IN
// ------------------------------
const protectedPages = ["home.html", "chat.html", "contributor.html"];
if(protectedPages.includes(window.location.pathname.split("/").pop()) && !localStorage.getItem("token")) {
  window.location = "index.html";
}

// ------------------------------
// CHAT FUNCTIONALITY
// ------------------------------
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const messagesEl = document.getElementById("messages");

if(chatForm) {
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = chatInput.value.trim();
    if(!message) return;

    addMessageToUI(message, "user");
    chatInput.value = "";

    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + token
        },
        body: JSON.stringify({ message, history: [] })
      });

      const data = await res.json();
      if(res.ok) {
        addMessageToUI(data.answer, "ai");
      } else {
        addMessageToUI("❌ " + (data.detail || "Error from server"), "ai");
      }
    } catch(err) {
      console.error(err);
      addMessageToUI("❌ Failed to send message", "ai");
    }

    messagesEl.scrollTop = messagesEl.scrollHeight;
  });
}

// ------------------------------
// HELPER: Add message to chat UI
// ------------------------------
function addMessageToUI(message, sender) {
  const bubble = document.createElement("div");
  bubble.className = `bubble ${sender}`;
  bubble.textContent = message;
  messagesEl.appendChild(bubble);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}
