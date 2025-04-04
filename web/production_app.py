"""
Production-ready web application for the multimodal RAG chatbot
"""

import os
import sys
import logging
import tempfile
import uuid
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# FastAPI imports
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# Create FastAPI app
app = FastAPI(title="Multimodal RAG Chatbot", description="Enterprise assistance chatbot with multimodal capabilities")

# Create static directory
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, "uploads"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Create CSS file
css_content = """
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f8f9fa;
}
.chat-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}
.chat-header {
    background-color: #0d6efd;
    color: white;
    padding: 15px 20px;
    border-radius: 10px 10px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.chat-header h1 {
    margin: 0;
    font-size: 1.5rem;
}
.chat-messages {
    height: 60vh;
    overflow-y: auto;
    padding: 20px;
    background-color: white;
    border-left: 1px solid #dee2e6;
    border-right: 1px solid #dee2e6;
}
.message {
    margin-bottom: 15px;
    padding: 10px 15px;
    border-radius: 10px;
    max-width: 80%;
}
.user-message {
    background-color: #e9ecef;
    margin-left: auto;
    text-align: right;
}
.bot-message {
    background-color: #f1f8ff;
    margin-right: auto;
}
.chat-input {
    display: flex;
    padding: 15px;
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-top: none;
    border-radius: 0 0 10px 10px;
}
.chat-input input {
    flex-grow: 1;
    padding: 10px 15px;
    border: 1px solid #ced4da;
    border-radius: 5px;
    margin-right: 10px;
}
.chat-input button {
    padding: 10px 20px;
}
.file-upload {
    margin-bottom: 15px;
    padding: 15px;
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 10px;
}
.media-preview {
    max-width: 300px;
    max-height: 200px;
    margin-top: 10px;
    border-radius: 5px;
}
.loading {
    display: none;
    text-align: center;
    margin: 20px 0;
}
.loading-spinner {
    width: 3rem;
    height: 3rem;
}
.message-media {
    max-width: 250px;
    max-height: 150px;
    border-radius: 5px;
    margin-top: 10px;
}
.use-case-badge {
    font-size: 0.8rem;
    padding: 3px 8px;
    border-radius: 10px;
    background-color: #6c757d;
    color: white;
    margin-left: 10px;
}
.reset-btn {
    margin-left: 10px;
}
"""

with open(os.path.join(static_dir, "css", "style.css"), "w") as f:
    f.write(css_content)

# Create JavaScript file
js_content = """
document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const resetBtn = document.getElementById('resetBtn');
    const fileUpload = document.getElementById('fileUpload');
    const imagePreview = document.getElementById('imagePreview');
    const audioPreview = document.getElementById('audioPreview');
    const videoPreview = document.getElementById('videoPreview');
    const mediaPreviewContainer = document.getElementById('mediaPreviewContainer');
    const loadingIndicator = document.getElementById('loadingIndicator');
    
    // Handle file upload preview
    fileUpload.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) {
            mediaPreviewContainer.style.display = 'none';
            return;
        }
        
        const fileType = file.type.split('/')[0];
        
        // Reset all previews
        imagePreview.style.display = 'none';
        audioPreview.style.display = 'none';
        videoPreview.style.display = 'none';
        
        if (fileType === 'image') {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                imagePreview.style.display = 'block';
                mediaPreviewContainer.style.display = 'block';
            };
            reader.readAsDataURL(file);
        } else if (fileType === 'audio') {
            const url = URL.createObjectURL(file);
            audioPreview.src = url;
            audioPreview.style.display = 'block';
            mediaPreviewContainer.style.display = 'block';
        } else if (fileType === 'video') {
            const url = URL.createObjectURL(file);
            videoPreview.src = url;
            videoPreview.style.display = 'block';
            mediaPreviewContainer.style.display = 'block';
        } else {
            // For documents, just show the filename
            const docPreview = document.createElement('div');
            docPreview.textContent = `Fichier sélectionné: ${file.name}`;
            mediaPreviewContainer.innerHTML = '';
            mediaPreviewContainer.appendChild(docPreview);
            mediaPreviewContainer.style.display = 'block';
        }
    });
    
    // Send message function
    function sendMessage() {
        const message = userInput.value.trim();
        if (message === '' && !fileUpload.files[0]) return;
        
        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input
        userInput.value = '';
        
        // Show loading indicator
        loadingIndicator.style.display = 'block';
        
        // Prepare form data
        const formData = new FormData();
        formData.append('query', message);
        
        if (fileUpload.files[0]) {
            formData.append('file', fileUpload.files[0]);
            
            // Store file info for display
            const fileInfo = {
                type: fileUpload.files[0].type.split('/')[0],
                url: URL.createObjectURL(fileUpload.files[0])
            };
            
            // Reset file upload
            mediaPreviewContainer.style.display = 'none';
            fileUpload.value = '';
        }
        
        // Simulate response for demo
        setTimeout(() => {
            // Hide loading indicator
            loadingIndicator.style.display = 'none';
            
            // Add bot response to chat
            const demoResponses = [
                "Voici les informations que j'ai trouvées dans la base de connaissances concernant votre question. Les procédures d'onboarding sont disponibles dans le document 'Onboarding_Procedures.pdf' sur le SharePoint de l'entreprise.",
                "D'après la documentation technique, la pièce que vous montrez sur l'image est une valve de régulation modèle TR-7500. Vous trouverez le guide de maintenance dans la section 'Équipements industriels' du portail technique.",
                "Pour résoudre ce problème de connexion, veuillez vérifier que votre VPN est actif et que vous utilisez les identifiants du domaine principal. Si le problème persiste, contactez le support IT au poste 4500.",
                "J'ai trouvé plusieurs documents pertinents concernant votre demande. Le plus récent est la note de service du 15 mars concernant les nouvelles procédures de demande de congés. Souhaitez-vous que je vous en fournisse un résumé?"
            ];
            
            const randomResponse = demoResponses[Math.floor(Math.random() * demoResponses.length)];
            
            addMessage(randomResponse, 'bot', {
                use_case: ['employee_assistance', 'knowledge_management', 'maintenance', 'helpdesk'][Math.floor(Math.random() * 4)]
            });
            
            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 1500);
    }
    
    // Add message to chat
    function addMessage(text, sender, data = null) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
        
        // Add message text
        messageDiv.textContent = text;
        
        // If it's a bot message and we have use case info, add a badge
        if (sender === 'bot' && data && data.use_case) {
            const useCaseBadge = document.createElement('span');
            useCaseBadge.classList.add('use-case-badge');
            
            let useCaseLabel = 'Général';
            switch(data.use_case) {
                case 'employee_assistance':
                    useCaseLabel = 'RH';
                    break;
                case 'knowledge_management':
                    useCaseLabel = 'Documentation';
                    break;
                case 'maintenance':
                    useCaseLabel = 'Maintenance';
                    break;
                case 'helpdesk':
                    useCaseLabel = 'IT Support';
                    break;
                case 'multimodal':
                    useCaseLabel = 'Multimodal';
                    break;
            }
            
            useCaseBadge.textContent = useCaseLabel;
            messageDiv.appendChild(document.createElement('br'));
            messageDiv.appendChild(useCaseBadge);
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    resetBtn.addEventListener('click', function() {
        // Reset conversation
        // Clear chat messages except the first one (welcome message)
        while (chatMessages.children.length > 1) {
            chatMessages.removeChild(chatMessages.lastChild);
        }
        
        // Add system message
        addMessage('Nouvelle conversation démarrée.', 'bot');
    });
});
"""

with open(os.path.join(static_dir, "js", "script.js"), "w") as f:
    f.write(js_content)

# Create HTML file
html_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Assistant d'Entreprise Multimodal</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="/static/css/style.css" rel="stylesheet">
</head>
<body>
    <div class="container chat-container">
        <div class="chat-header">
            <h1>Assistant d'Entreprise Multimodal</h1>
            <button id="resetBtn" class="btn btn-sm btn-outline-light reset-btn">Nouvelle conversation</button>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">
                Bonjour ! Je suis votre assistant d'entreprise multimodal. Je peux vous aider avec :
                <ul>
                    <li>Assistance aux employés (RH, IT, logistique)</li>
                    <li>Recherche documentaire et gestion des connaissances</li>
                    <li>Maintenance et diagnostic technique</li>
                    <li>Support informatique interne</li>
                </ul>
                Vous pouvez également m'envoyer des images, des fichiers audio ou vidéo pour une assistance plus précise.
            </div>
        </div>
        
        <div class="file-upload">
            <div class="mb-3">
                <label for="fileUpload" class="form-label">Joindre un fichier (optionnel)</label>
                <input class="form-control" type="file" id="fileUpload" accept=".jpg,.jpeg,.png,.gif,.pdf,.docx,.pptx,.xlsx,.mp3,.wav,.mp4,.avi">
            </div>
            <div id="mediaPreviewContainer" style="display: none;">
                <img id="imagePreview" class="media-preview" style="display: none;">
                <audio id="audioPreview" class="media-preview" controls style="display: none;"></audio>
                <video id="videoPreview" class="media-preview" controls style="display: none;"></video>
            </div>
        </div>
        
        <div class="chat-input">
            <input type="text" id="userInput" placeholder="Tapez votre message ici..." class="form-control">
            <button id="sendBtn" class="btn btn-primary">Envoyer</button>
        </div>
        
        <div class="loading" id="loadingIndicator">
            <div class="spinner-border loading-spinner text-primary" role="status">
                <span class="visually-hidden">Chargement...</span>
            </div>
            <p>Traitement en cours...</p>
        </div>
    </div>

    <script src="/static/js/script.js"></script>
</body>
</html>
"""

with open(os.path.join(static_dir, "index.html"), "w") as f:
    f.write(html_content)

@app.get("/")
async def index():
    """Serve the static index.html file"""
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
