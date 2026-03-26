// ── Tab switching ─────────────────────────────────────────────────────────────
function showTab(tabId, btn) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    document.getElementById(tabId).style.display = 'block';

    document.querySelectorAll('.tabs button').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
}

// ── Auth ──────────────────────────────────────────────────────────────────────
let currentToken = null;

// STEP 1: POST /login → get token
async function login() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    if (!username || !password) {
        showAuthMessage("Enter a username and password first.", "error");
        return;
    }

    try {
        const res = await fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });

        if (res.ok) {
            const data = await res.json();
            currentToken = data.token;
            document.getElementById("token").value = currentToken; // auto-fill
            showAuthMessage("Token issued — click Verify Token to authenticate.", "success");
        } else {
            showAuthMessage("Login failed. Check your username and password.", "error");
        }
    } catch {
        showAuthMessage("Network error. Is the server running?", "error");
    }
}

// STEP 2: POST /verify → unlock video
async function authenticate() {
    const username = document.getElementById("username").value.trim();
    const token    = document.getElementById("token").value.trim();

    if (!username || !token) {
        showAuthMessage("Enter your username and token, then click Verify Token.", "error");
        return;
    }

    try {
        const res = await fetch("/verify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, token }),
        });

        if (res.ok) {
            document.getElementById("authSection").style.display = "none";
            document.getElementById("obiwanVideo").style.display = "block";
        } else {
            showAuthMessage("Invalid or expired token. Use Get Token to request a new one.", "error");
        }
    } catch {
        showAuthMessage("Network error. Is the server running?", "error");
    }
}

function showAuthMessage(msg, type) {
    const el = document.getElementById("authMessage");
    if (!el) return;
    el.textContent = msg;
    el.className = "auth-message " + type;
}

// ── Images ───────────────────────────────────────────────────────────────────
async function loadImages() {
    const gallery    = document.getElementById("imageGallery");
    const imageCount = document.getElementById("imageCount");

    gallery.innerHTML = '<div class="loading">Scanning for vulnerabilities</div>';

    try {
        const res  = await fetch("/images.json?t=" + Date.now());
        const data = await res.json();
        const imgs = data.images || [];

        if (imgs.length === 0) {
            gallery.innerHTML = '<div class="error">No vulnerability images detected</div>';
            imageCount.textContent = "No images detected";
            return;
        }

        imageCount.textContent = `${imgs.length} vulnerability image${imgs.length !== 1 ? "s" : ""} detected`;
        gallery.innerHTML = "";
        imgs.forEach((img, i) => gallery.appendChild(createImageCard(img.path, img.filename, i + 1)));

    } catch {
        gallery.innerHTML = '<div class="error">Failed to load image manifest</div>';
        imageCount.textContent = "Error loading images";
    }
}

function createImageCard(path, filename, index) {
    const card = document.createElement("div");
    card.className = "image-card";
    card.innerHTML = `
        <img src="${path}" loading="lazy" alt="Vulnerability #${index}">
        <div class="image-info">
            <div class="image-name">Vulnerability #${index}</div>
            <div class="image-meta">${filename}</div>
        </div>
    `;
    card.addEventListener("click", () => window.open(path, "_blank"));
    return card;
}

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    loadImages();
    const firstBtn = document.querySelector(".tabs button");
    if (firstBtn) firstBtn.classList.add("active");
});