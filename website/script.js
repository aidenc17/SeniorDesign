// ── Tab switching ─────────────────────────────────────────────────────────────
function showTab(tabId, btn) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    document.getElementById(tabId).style.display = 'block';

    document.querySelectorAll('.tabs button').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
}

// ── Auth state ────────────────────────────────────────────────────────────────
let currentUsername = "";

// STEP 1: POST /login → sends OTP email
async function login() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    if (!username || !password) {
        showAuthMessage("Enter your email and password first.", "error");
        return;
    }

    showAuthMessage("Sending code...", "");

    try {
        const res  = await fetch("/login", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({ username, password }),
        });
        const data = await res.json();

        if (res.ok && data.success) {
            currentUsername = username;
            // Show OTP step
            document.getElementById("step1").style.display = "none";
            document.getElementById("step2").style.display = "block";
            showOtpMessage("Code sent — check your email.", "success");
        } else {
            showAuthMessage("Login failed. Check your email and password.", "error");
        }
    } catch {
        showAuthMessage("Network error. Is the server running?", "error");
    }
}

// STEP 2: POST /verify-otp → unlock video
async function verifyOtp() {
    const otp = document.getElementById("otpInput").value.trim();

    if (!otp) {
        showOtpMessage("Enter the 6-digit code from your email.", "error");
        return;
    }

    showOtpMessage("Verifying...", "");

    try {
        const res  = await fetch("/verify-otp", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({ username: currentUsername, otp }),
        });
        const data = await res.json();

        if (res.ok && data.success) {
            document.getElementById("authSection").style.display = "none";
            document.getElementById("obiwanVideo").style.display = "block";
        } else {
            showOtpMessage(data.error || "Invalid or expired code.", "error");
        }
    } catch {
        showOtpMessage("Network error. Is the server running?", "error");
    }
}

// Back button — return to step 1
function resetAuth() {
    currentUsername = "";
    document.getElementById("step2").style.display  = "none";
    document.getElementById("step1").style.display  = "block";
    document.getElementById("otpInput").value       = "";
    showOtpMessage("", "");
    showAuthMessage("", "");
}

function showAuthMessage(msg, type) {
    const el = document.getElementById("authMessage");
    if (!el) return;
    el.textContent = msg;
    el.className   = "auth-message " + type;
}

function showOtpMessage(msg, type) {
    const el = document.getElementById("otpMessage");
    if (!el) return;
    el.textContent = msg;
    el.className   = "auth-message " + type;
}

// ── Images ────────────────────────────────────────────────────────────────────
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