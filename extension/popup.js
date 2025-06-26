// Configuration
const API_BASE_URL = 'http://localhost:8000';

// Éléments DOM
let jobContent = '';
let jobTitle = '';
let jobUrl = '';
let availableCVs = [];

// Initialisation
document.addEventListener('DOMContentLoaded', async () => {
    await extractJobContent();
    await loadAvailableCVs();
    setupEventListeners();
    checkApiStatus();
});

// Extraction du contenu de l'offre d'emploi
async function extractJobContent() {
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        console.log('Tentative d\'extraction depuis:', tab.url);
        
        const response = await chrome.tabs.sendMessage(tab.id, { action: 'extractContent' });
        
        console.log('Réponse reçue:', response);
        
        if (response && response.success && response.content && response.content.length > 50) {
            jobContent = response.content;
            jobTitle = response.title;
            jobUrl = response.url;
            
            // Afficher les informations de l'offre
            document.getElementById('jobInfo').style.display = 'block';
            document.getElementById('jobTitle').textContent = jobTitle;
            document.getElementById('jobUrl').textContent = jobUrl;
            
            showStatus(`Offre détectée: ${response.content.length} caractères`, 'success');
            console.log('Contenu détecté:', response.content.substring(0, 200) + '...');
            
            // Mettre à jour l'état du bouton
            updateGenerateButton();
        } else {
            showStatus(`Impossible de détecter l'offre sur cette page. URL: ${tab.url}`, 'error');
            console.log('Échec de la détection:', response);
        }
    } catch (error) {
        console.error('Erreur lors de l\'extraction:', error);
        showStatus('Erreur lors de l\'extraction du contenu', 'error');
    }
}

// Configuration des événements
function setupEventListeners() {
    // Éléments
    const cvFileInput = document.getElementById('cvFile');
    const fileLabel = document.getElementById('fileLabel');
    const generateBtn = document.getElementById('generateBtn');
    const cvSelect = document.getElementById('cvSelect');
    const useExistingCV = document.getElementById('useExistingCV');
    const useNewCV = document.getElementById('useNewCV');
    
    // Upload de fichier CV
    cvFileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            if (file.type === 'application/pdf') {
                fileLabel.textContent = `✅ ${file.name}`;
                updateGenerateButton();
                showStatus('CV sélectionné avec succès', 'success');
            } else {
                showStatus('Veuillez sélectionner un fichier PDF', 'error');
                updateGenerateButton();
            }
        } else {
            fileLabel.textContent = 'Cliquez pour sélectionner votre CV';
            updateGenerateButton();
        }
    });
    
    // Sélection de CV existant
    cvSelect.addEventListener('change', updateGenerateButton);
    
    // Basculement entre CV existant/nouveau
    useExistingCV.addEventListener('change', toggleCVSource);
    useNewCV.addEventListener('change', toggleCVSource);
    
    // Génération de la lettre
    generateBtn.addEventListener('click', generateCoverLetter);
}

// Vérification du statut de l'API
async function checkApiStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('API disponible');
        } else {
            showStatus('API non disponible. Démarrez le serveur backend.', 'error');
        }
    } catch (error) {
        showStatus('Impossible de contacter l\'API. Vérifiez que le serveur est démarré.', 'error');
    }
}

// Chargement des CV disponibles
async function loadAvailableCVs() {
    try {
        console.log('Chargement des CV disponibles...');
        const response = await fetch(`${API_BASE_URL}/cv/list`);
        
        if (response.ok) {
            const data = await response.json();
            availableCVs = data.cvs || [];
            
            console.log('CV disponibles:', availableCVs);
            populateCVSelect();
            
            // Présélectionner le dernier CV utilisé s'il y en a un
            if (availableCVs.length > 0) {
                document.getElementById('useExistingCV').checked = true;
                document.getElementById('useNewCV').checked = false;
                toggleCVSource();
            }
        } else {
            console.log('Aucun CV disponible ou erreur de récupération');
            availableCVs = [];
            populateCVSelect();
        }
    } catch (error) {
        console.error('Erreur lors du chargement des CV:', error);
        availableCVs = [];
        populateCVSelect();
    }
}

// Peupler la liste déroulante des CV
function populateCVSelect() {
    const cvSelect = document.getElementById('cvSelect');
    cvSelect.innerHTML = '';
    
    if (availableCVs.length === 0) {
        cvSelect.innerHTML = '<option value="">Aucun CV disponible</option>';
        return;
    }
    
    cvSelect.innerHTML = '<option value="">Sélectionnez un CV</option>';
    
    availableCVs.forEach(cv => {
        const option = document.createElement('option');
        option.value = cv.id;
        
        // Afficher le nom original + date
        const uploadDate = new Date(cv.upload_date).toLocaleDateString('fr-FR');
        option.textContent = `${cv.original_filename} (${uploadDate})`;
        
        cvSelect.appendChild(option);
    });
    
    // Présélectionner le premier CV (le plus récemment utilisé)
    if (availableCVs.length > 0) {
        cvSelect.value = availableCVs[0].id;
    }
}

// Basculer entre CV existant et nouveau CV
function toggleCVSource() {
    const useExisting = document.getElementById('useExistingCV').checked;
    const existingSection = document.getElementById('existingCVSection');
    const newSection = document.getElementById('newCVSection');
    
    if (useExisting) {
        existingSection.classList.remove('hidden');
        newSection.classList.add('hidden');
    } else {
        existingSection.classList.add('hidden');
        newSection.classList.remove('hidden');
    }
    
    updateGenerateButton();
}

// Mettre à jour l'état du bouton générer
function updateGenerateButton() {
    const generateBtn = document.getElementById('generateBtn');
    const useExisting = document.getElementById('useExistingCV').checked;
    const cvSelect = document.getElementById('cvSelect');
    const cvFile = document.getElementById('cvFile');
    
    let canGenerate = false;
    
    if (useExisting) {
        // CV existant sélectionné
        canGenerate = cvSelect.value !== '';
    } else {
        // Nouveau CV
        canGenerate = cvFile.files.length > 0 && cvFile.files[0].type === 'application/pdf';
    }
    
    // Vérifier aussi qu'une offre est détectée
    canGenerate = canGenerate && jobContent && jobContent.length > 50;
    
    generateBtn.disabled = !canGenerate;
}

// Génération de la lettre de motivation
async function generateCoverLetter() {
    const generateBtn = document.getElementById('generateBtn');
    const loading = document.getElementById('loading');
    const useExisting = document.getElementById('useExistingCV').checked;
    
    console.log('Début génération:');
    console.log('- Mode:', useExisting ? 'CV existant' : 'Nouveau CV');
    console.log('- Contenu offre:', jobContent ? jobContent.length + ' caractères' : 'AUCUN');
    console.log('- URL:', jobUrl);
    
    // Vérifier les prérequis
    if (!jobContent || jobContent.length < 50) {
        showStatus('Aucune offre d\'emploi détectée sur cette page. Essayez de recharger la page.', 'error');
        return;
    }
    
    let cvFile = null;
    let cvId = null;
    
    if (useExisting) {
        // Utiliser un CV existant
        cvId = document.getElementById('cvSelect').value;
        if (!cvId) {
            showStatus('Veuillez sélectionner un CV existant', 'error');
            return;
        }
        console.log('- CV existant sélectionné:', cvId);
    } else {
        // Utiliser un nouveau CV
        cvFile = document.getElementById('cvFile').files[0];
        if (!cvFile) {
            showStatus('Veuillez sélectionner un fichier CV (PDF)', 'error');
            return;
        }
        console.log('- Nouveau CV sélectionné:', cvFile.name);
    }
    
    // Afficher le loading
    generateBtn.disabled = true;
    loading.style.display = 'block';
    showStatus('Génération en cours...', 'info');
    
    try {
        // Détecter la langue
        console.log('Détection de la langue...');
        const langResponse = await fetch(`${API_BASE_URL}/detect-language`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `content=${encodeURIComponent(jobContent)}`
        });
        
        const langData = await langResponse.json();
        const langue = langData.langue || 'en';
        console.log('Langue détectée:', langue);
        
        // Préparer les données
        const formData = new FormData();
        formData.append('offre_content', jobContent);
        formData.append('langue', langue);
        
        if (cvId) {
            // Utiliser CV existant
            formData.append('cv_id', cvId);
        } else if (cvFile) {
            // Utiliser nouveau CV
            formData.append('cv_file', cvFile);
        }
        
        console.log('Envoi vers l\'API...');
        
        // Envoyer la requête
        const response = await fetch(`${API_BASE_URL}/generate-letter`, {
            method: 'POST',
            body: formData
        });
        
        console.log('Réponse API:', response.status);
        
        if (response.ok) {
            // L'API retourne maintenant un PDF directement
            const pdfBlob = await response.blob();
            console.log('PDF reçu, taille:', pdfBlob.size);
            
            // Si un nouveau CV a été utilisé, recharger la liste
            if (cvFile && !cvId) {
                await loadAvailableCVs();
            }
            
            // Télécharger le PDF
            downloadPDF(pdfBlob, `lettre_motivation_${jobTitle.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`);
            showStatus(`Lettre PDF générée avec succès en ${langue} !`, 'success');
        } else {
            const error = await response.text();
            console.error('Erreur API:', error);
            showStatus(`Erreur API: ${error}`, 'error');
        }
        
    } catch (error) {
        console.error('Erreur:', error);
        showStatus('Erreur de connexion avec l\'API. Vérifiez que le serveur est démarré.', 'error');
    } finally {
        generateBtn.disabled = false;
        loading.style.display = 'none';
    }
}

// Téléchargement de la lettre (texte - fonction conservée pour compatibilité)
function downloadLetter(content, filename) {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    
    // Créer un lien de téléchargement temporaire
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    
    // Nettoyer
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Téléchargement du PDF
function downloadPDF(pdfBlob, filename) {
    const url = URL.createObjectURL(pdfBlob);
    
    // Créer un lien de téléchargement temporaire
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    
    // Nettoyer
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Affichage des messages de statut
function showStatus(message, type) {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
    statusDiv.style.display = 'block';
    
    // Masquer après 5 secondes sauf pour les erreurs
    if (type !== 'error') {
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 5000);
    }
}
