const form = document.getElementById('task-form');
const statusEl = document.getElementById('status');
const listEl = document.getElementById('task-list');

async function loadTasks() {
  const res = await fetch('/api/tasks');
  const body = await res.json();
  if (!res.ok || !Array.isArray(body)) {
    statusEl.textContent = `Error: ${body.message || 'Failed to load tasks'}`;
    return;
  }
  listEl.innerHTML = body
    .map(
      (t) => `
        <li class="task-item ${t.completed ? 'completed' : ''}" data-id="${t.id}">
          <input type="checkbox" ${t.completed ? 'checked' : ''} onchange="toggleTask(${t.id}, this.checked)" />
          <div class="task-body">
            <div class="task-title">${escapeHtml(t.title)}</div>
            ${t.description ? `<div class="task-description">${escapeHtml(t.description)}</div>` : ''}
          </div>
          <div class="task-actions">
            <button onclick="deleteTask(${t.id})">Delete</button>
          </div>
        </li>
      `
    )
    .join('');
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const submitBtn = form.querySelector('button');
  submitBtn.disabled = true;
  statusEl.textContent = 'Saving...';

  try {
    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;
    const res = await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, description, completed: false }),
    });
    if (!res.ok) throw new Error('Failed to create task');
    statusEl.textContent = 'Added!';
    form.reset();
    await loadTasks();
  } catch (err) {
    statusEl.textContent = `Error: ${err.message}`;
  } finally {
    submitBtn.disabled = false;
  }
});

async function toggleTask(id, completed) {
  const res = await fetch(`/api/tasks/${id}`);
  const task = await res.json();
  await fetch(`/api/tasks/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: task.title, description: task.description, completed }),
  });
  await loadTasks();
}

async function deleteTask(id) {
  await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
  await loadTasks();
}

loadTasks();
