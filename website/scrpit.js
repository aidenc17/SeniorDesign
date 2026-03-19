const RECEIVED_IMAGES_PATH = '../received_images/';

// load and display images
async function loadImages() {
    const gallery = document.getElementById('imageGallery');
    const imageCount = document.getElementById('imageCount');
    
    try {
        // get list of images from the received_images folder
        // since we can't list directory contents directly in browser,
        // we'll try to load images by expected filenames
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

// attempt to find available images
async function findAvailableImages() {
    const possibleImages = [];
    
    //common naming patterns
    const patterns = [
        // Pattern 1: image1.png, image2.png, etc.
        ...Array.from({length: 20}, (_, i) => `image${i + 1}.png`),
        // Pattern 2: circle 1.png, circle 2.png, etc.
        ...Array.from({length: 20}, (_, i) => `circle${i + 1}.png`)
    ];
    
    const foundImages = [];
    
    for (const filename of patterns) {
        const path = RECEIVED_IMAGES_PATH + filename;
        if (await imageExists(path)) {
            foundImages.push(path);
        }
    }
    
    return foundImages;
}

// check if image exists
function imageExists(url) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => resolve(true);
        img.onerror = () => resolve(false);
        img.src = url;
    });
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
    
    // Click to view full size
    card.addEventListener('click', () => {
        window.open(imagePath, '_blank');
    });
    
    return card;
}

// initialize on page load
document.addEventListener('DOMContentLoaded', loadImages);