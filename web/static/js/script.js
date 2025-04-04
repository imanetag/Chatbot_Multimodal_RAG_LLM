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
