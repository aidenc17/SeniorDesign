// TAB SWITCHING
function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    document.getElementById(tabId).style.display = 'block';
}

// AUTHENTICATION
let currentToken = null;

// STEP 1: LOGIN
async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ username, password })
    });

    if (res.ok) {
        const data = await res.json();
        currentToken = data.token;

        alert("Token generated:\n" + currentToken);
    } else {
        alert("Login failed");
    }
}

// STEP 2: VERIFY
async function authenticate() {
    const username = document.getElementById("username").value;
    const token = document.getElementById("token").value;

    const res = await fetch("/verify", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ username, token })
    });

    if (res.ok) {
        document.getElementById("obiwanVideo").style.display = "block";
        alert("Access granted.");
    } else {
        alert("Invalid or expired token.");
    }
}

// load and display images
async function loadImages() {
    const gallery = document.getElementById('imageGallery');
    const imageCount = document.getElementById('imageCount');
    
    try {
        const images = await findAvailableImages();
        
        if (images.length === 0) {
            gallery.innerHTML = '<div class="error">No images found</div>';
            imageCount.textContent = 'No images detected';
            return;
        }
        
        imageCount.textContent = `${images.length} vulnerability images detected`;
        gallery.innerHTML = '';
        
        images.forEach((imagePath, index) => {
            const card = createImageCard(imagePath, index + 1);
            gallery.appendChild(card);
        });
        
    } catch (error) {
        gallery.innerHTML = '<div class="error">Error loading images</div>';
        imageCount.textContent = 'Error loading images';
    }
}

async function findAvailableImages() {
    const response = await fetch("images.json?t=" + Date.now());
    const data = await response.json();
    return data.images.map(img => img.path);
}

function createImageCard(imagePath, index) {
    const card = document.createElement('div');
    card.className = 'image-card';
    
    const filename = imagePath.split('/').pop();
    
    card.innerHTML = `
        <img src="${imagePath}" loading="lazy">
        <div class="image-info">
            <div class="image-name">Vulnerability #${index}</div>
            <div class="image-meta">${filename}</div>
        </div>
    `;
    
    card.addEventListener('click', () => {
        window.open(imagePath, '_blank');
    });
    
    return card;
}

document.addEventListener('DOMContentLoaded', loadImages);