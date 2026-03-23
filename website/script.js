// load and display images
async function loadImages() {
    const gallery = document.getElementById('imageGallery');
    const imageCount = document.getElementById('imageCount');
    
    try {
        // Load actual image list from JSON (no guessing)
        const images = await findAvailableImages();
        
        if (images.length === 0) {
            gallery.innerHTML = '<div class="error">No images found in received_images folder</div>';
            imageCount.textContent = 'No images detected';
            return;
        }
        
        // update status
        imageCount.textContent = `${images.length} vulnerability images detected`;
        
        // clear loading state
        gallery.innerHTML = '';
        
        // create image cards
        images.forEach((imagePath, index) => {
            const card = createImageCard(imagePath, index + 1);
            gallery.appendChild(card);
        });
        
    } catch (error) {
        console.error('Error loading images:', error);
        gallery.innerHTML = '<div class="error">Error loading images. Check console for details.</div>';
        imageCount.textContent = 'Error loading images';
    }
}

// get images directly from images.json
async function findAvailableImages() {
    const response = await fetch("images.json?t=" + Date.now()); // prevent caching
    const data = await response.json();

    return data.images.map(img => img.path);
}

// creates image card element
function createImageCard(imagePath, index) {
    const card = document.createElement('div');
    card.className = 'image-card';
    
    const filename = imagePath.split('/').pop();
    
    card.innerHTML = `
        <img src="${imagePath}" alt="Vulnerability ${index}" loading="lazy">
        <div class="image-info">
            <div class="image-name">Vulnerability #${index}</div>
            <div class="image-meta">${filename}</div>
        </div>
    `;
    
    // click to view full size
    card.addEventListener('click', () => {
        window.open(imagePath, '_blank');
    });
    
    return card;
}

// initialize on page load
document.addEventListener('DOMContentLoaded', loadImages);