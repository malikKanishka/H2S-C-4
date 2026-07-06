'use strict';

const form     = document.getElementById('login-form');
const btnLogin = document.getElementById('btn-login');
const errorMsg = document.getElementById('error-msg');
const errorTxt = document.getElementById('error-text');

// ---- Toggle password visibility ----
document.getElementById('toggle-pw')?.addEventListener('click', () => {
  const pw = document.getElementById('password');
  const icon = document.getElementById('eye-icon');
  if (pw.type === 'password') {
    pw.type = 'text';
    icon.innerHTML = `<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
      <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
      <line x1="1" y1="1" x2="23" y2="23"/>`;
  } else {
    pw.type = 'password';
    icon.innerHTML = `<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>`;
  }
});

// ---- Demo credential chips ----
document.querySelectorAll('.chip').forEach(chip => {
  chip.addEventListener('click', () => {
    document.getElementById('username').value = chip.dataset.user;
    document.getElementById('password').value = chip.dataset.pass;
    hideError();
    // Visual feedback
    document.querySelectorAll('.chip').forEach(c => c.style.opacity = '0.5');
    chip.style.opacity = '1';
    chip.style.transform = 'translateY(-3px)';
    setTimeout(() => {
      document.querySelectorAll('.chip').forEach(c => {
        c.style.opacity = '1';
        c.style.transform = '';
      });
    }, 600);
  });
});

function showError(msg) {
  errorTxt.textContent = msg;
  errorMsg.hidden = false;
}
function hideError() {
  errorMsg.hidden = true;
}

function setLoading(on) {
  btnLogin.disabled = on;
  btnLogin.querySelector('.btn-label').hidden = on;
  btnLogin.querySelector('.btn-spinner').hidden = !on;
}

// ---- Login form submit ----
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  hideError();

  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;

  if (!username || !password) {
    showError('Please enter your username and password.');
    return;
  }

  setLoading(true);

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();

    if (res.ok && data.access_token) {
      const token = data.access_token;
      // Redirect to dashboard with token
      window.location.href = `/dashboard?token=${encodeURIComponent(token)}`;
    } else {
      const msg = data.error === 'invalid_credentials'
        ? 'Invalid username or password.'
        : data.error || 'Login failed. Please try again.';
      showError(msg);
      setLoading(false);
    }
  } catch (err) {
    showError('Network error. Is the server running?');
    setLoading(false);
  }
});

// ---- Auto-focus first input ----
document.getElementById('username')?.focus();
