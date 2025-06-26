// Fonction pour extraire le contenu de l'offre d'emploi
function extractJobContent() {
    let content = '';
    
    // Stratégies d'extraction selon le site
    const selectors = [
        // JobTeaser
        '.job-description',
        '[data-testid="job-description"]',
        '.offer-description',
        
        // LinkedIn
        '.jobs-description-content__text',
        '.jobs-box__html-content',
        
        // Indeed
        '.jobsearch-jobDescriptionText',
        '#jobDescriptionText',
        
        // Générique
        '[class*="description"]',
        '[class*="content"]',
        '[id*="description"]',
        'main',
        'article',
        '.job-detail',
        '.job-content'
    ];
    
    // Essayer chaque sélecteur
    for (const selector of selectors) {
        const element = document.querySelector(selector);
        if (element && element.textContent.trim().length > 100) {
            content = element.textContent.trim();
            break;
        }
    }
    
    // Si aucun sélecteur spécifique ne fonctionne, prendre le contenu principal
    if (!content || content.length < 100) {
        const bodyText = document.body.textContent || document.body.innerText || '';
        const lines = bodyText.split('\n')
            .map(line => line.trim())
            .filter(line => line.length > 5 && !line.includes('Cookie') && !line.includes('JavaScript'));
        content = lines.join(' ').substring(0, 5000);
    }
    
    return content;
}

// Fonction pour détecter le titre du poste
function extractJobTitle() {
    const titleSelectors = [
        'h1',
        '.job-title',
        '[data-testid="job-title"]',
        '.position-title',
        '.offer-title'
    ];
    
    for (const selector of titleSelectors) {
        const element = document.querySelector(selector);
        if (element && element.textContent.trim()) {
            return element.textContent.trim();
        }
    }
    return 'Poste non identifié';
}

// Écouter les messages depuis la popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'extractContent') {
        const jobContent = extractJobContent();
        const jobTitle = extractJobTitle();
        const url = window.location.href;
        
        sendResponse({
            content: jobContent,
            title: jobTitle,
            url: url,
            success: jobContent.length > 50
        });
    }
});

// Injecter un indicateur visuel quand l'extension est active
function showExtensionIndicator() {
    if (document.getElementById('cover-letter-indicator')) return;
    
    const indicator = document.createElement('div');
    indicator.id = 'cover-letter-indicator';
    indicator.innerHTML = '📝 Extension Lettre de Motivation active';
    indicator.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        background: #4CAF50;
        color: white;
        padding: 8px 12px;
        border-radius: 5px;
        font-size: 12px;
        z-index: 10000;
        font-family: Arial, sans-serif;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    `;
    
    document.body.appendChild(indicator);
    
    // Masquer après 3 secondes
    setTimeout(() => {
        if (indicator && indicator.parentNode) {
            indicator.parentNode.removeChild(indicator);
        }
    }, 3000);
}

// Afficher l'indicateur au chargement de la page
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', showExtensionIndicator);
} else {
    showExtensionIndicator();
}
