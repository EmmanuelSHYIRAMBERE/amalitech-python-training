// Serverless To-Do frontend — plain JS, no build step. Auth uses
// amazon-cognito-identity-js (loaded via CDN in index.html) for real
// SRP-based Cognito sign-up/sign-in; task CRUD calls the REST API
// directly with the Cognito ID token as a Bearer token, which API
// Gateway's Cognito authorizer validates.

const poolData = {
  UserPoolId: window.APP_CONFIG.userPoolId,
  ClientId: window.APP_CONFIG.userPoolClientId,
};
const userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);

let currentUser = null;
let idToken = null;

const authView = document.getElementById("auth-view");
const appView = document.getElementById("app-view");

function showApp() {
  authView.classList.add("hidden");
  appView.classList.remove("hidden");
  loadTasks();
}

function showAuth() {
  appView.classList.add("hidden");
  authView.classList.remove("hidden");
}

// ── Sign up ──────────────────────────────────
document.getElementById("signup-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const email = document.getElementById("signup-email").value;
  const password = document.getElementById("signup-password").value;
  const errorEl = document.getElementById("signup-error");
  errorEl.textContent = "";

  const attributeList = [
    new AmazonCognitoIdentity.CognitoUserAttribute({ Name: "email", Value: email }),
  ];

  userPool.signUp(email, password, attributeList, null, (err, result) => {
    if (err) {
      errorEl.textContent = err.message || JSON.stringify(err);
      return;
    }
    // Auto-confirmed server-side (PreSignUp Lambda) — sign in immediately.
    signIn(email, password, document.getElementById("signup-error"));
  });
});

// ── Sign in ──────────────────────────────────
document.getElementById("signin-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const email = document.getElementById("signin-email").value;
  const password = document.getElementById("signin-password").value;
  signIn(email, password, document.getElementById("signin-error"));
});

function signIn(email, password, errorEl) {
  errorEl.textContent = "";
  const authDetails = new AmazonCognitoIdentity.AuthenticationDetails({
    Username: email,
    Password: password,
  });
  const user = new AmazonCognitoIdentity.CognitoUser({ Username: email, Pool: userPool });

  user.authenticateUser(authDetails, {
    onSuccess: (session) => {
      currentUser = user;
      idToken = session.getIdToken().getJwtToken();
      showApp();
    },
    onFailure: (err) => {
      errorEl.textContent = err.message || JSON.stringify(err);
    },
  });
}

document.getElementById("signout-btn").addEventListener("click", () => {
  if (currentUser) currentUser.signOut();
  currentUser = null;
  idToken = null;
  showAuth();
});

// ── API calls ────────────────────────────────
async function apiFetch(path, options = {}) {
  const res = await fetch(`${window.APP_CONFIG.apiUrl}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: idToken,
      ...(options.headers || {}),
    },
  });
  if (res.status === 204) return null;
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.message || `Request failed: ${res.status}`);
  return body;
}

async function loadTasks() {
  try {
    const data = await apiFetch("/tasks");
    renderTasks(data.tasks || []);
  } catch (err) {
    console.error("Failed to load tasks", err);
  }
}

function renderTasks(tasks) {
  const lists = {
    Pending: document.getElementById("pending-list"),
    Completed: document.getElementById("completed-list"),
    Expired: document.getElementById("expired-list"),
  };
  Object.values(lists).forEach((ul) => (ul.innerHTML = ""));

  // Guard against a non-array response (e.g. an unexpected API error
  // shape) so one bad response can't crash the whole render.
  if (!Array.isArray(tasks)) return;

  for (const task of tasks) {
    const ul = lists[task.Status] || lists.Pending;
    const li = document.createElement("li");
    li.className = "task-item";
    li.innerHTML = `
      <span class="task-desc">${escapeHtml(task.Description)}</span>
      <span class="task-date">${escapeHtml(task.Date || "")}</span>
    `;

    if (task.Status === "Pending") {
      const completeBtn = document.createElement("button");
      completeBtn.textContent = "Complete";
      completeBtn.onclick = () => updateTask(task.TaskId, { Status: "Completed" });
      li.appendChild(completeBtn);
    }

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "Delete";
    deleteBtn.onclick = () => deleteTask(task.TaskId);
    li.appendChild(deleteBtn);

    ul.appendChild(li);
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

document.getElementById("task-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const description = document.getElementById("task-description").value;
  const date = document.getElementById("task-date").value;

  try {
    await apiFetch("/tasks", {
      method: "POST",
      body: JSON.stringify({ Description: description, Date: date || undefined }),
    });
    document.getElementById("task-description").value = "";
    document.getElementById("task-date").value = "";
    loadTasks();
  } catch (err) {
    alert(`Failed to create task: ${err.message}`);
  }
});

async function updateTask(taskId, fields) {
  try {
    await apiFetch(`/tasks/${taskId}`, {
      method: "PUT",
      body: JSON.stringify(fields),
    });
    loadTasks();
  } catch (err) {
    alert(`Failed to update task: ${err.message}`);
  }
}

async function deleteTask(taskId) {
  try {
    await apiFetch(`/tasks/${taskId}`, { method: "DELETE" });
    loadTasks();
  } catch (err) {
    alert(`Failed to delete task: ${err.message}`);
  }
}
