import React, { useState, useRef, useEffect } from 'react';
import './App.css';

// Define message types
interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  useCase?: string;
  fileUrl?: string;
  fileType?: string;
}

// Define file preview props
interface FilePreviewProps {
  file: File | null;
  onClear: () => void;
}

// File Preview Component
const FilePreview: React.FC<FilePreviewProps> = ({ file, onClear }) => {
  const [preview, setPreview] = useState<string | null>(null);
  
  useEffect(() => {
    if (!file) {
      setPreview(null);
      return;
    }
    
    const fileType = file.type.split('/')[0];
    
    if (fileType === 'image') {
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    } else if (fileType === 'audio' || fileType === 'video') {
      setPreview(URL.createObjectURL(file));
    }
    
    return () => {
      if (preview && (fileType === 'audio' || fileType === 'video')) {
        URL.revokeObjectURL(preview);
      }
    };
  }, [file]);
  
  if (!file) return null;
  
  const fileType = file.type.split('/')[0];
  
  return (
    <div className="mt-2 relative">
      <button 
        onClick={onClear}
        className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center"
      >
        ×
      </button>
      
      {fileType === 'image' && preview && (
        <img src={preview} alt="Preview" className="max-w-xs max-h-40 rounded-md" />
      )}
      
      {fileType === 'audio' && preview && (
        <audio src={preview} controls className="max-w-xs" />
      )}
      
      {fileType === 'video' && preview && (
        <video src={preview} controls className="max-w-xs max-h-40" />
      )}
      
      {!['image', 'audio', 'video'].includes(fileType) && (
        <div className="p-3 bg-gray-100 rounded-md">
          <span className="text-gray-700">Fichier: {file.name}</span>
        </div>
      )}
    </div>
  );
};

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Bonjour ! Je suis votre assistant d'entreprise multimodal. Je peux vous aider avec :\n- Assistance aux employés (RH, IT, logistique)\n- Recherche documentaire et gestion des connaissances\n- Maintenance et diagnostic technique\n- Support informatique interne\n\nVous pouvez également m'envoyer des images, des fichiers audio ou vidéo pour une assistance plus précise.",
      sender: 'bot'
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };
  
  // Clear selected file
  const clearSelectedFile = () => {
    setSelectedFile(null);
  };
  
  // Send message
  const sendMessage = () => {
    if (inputText.trim() === '' && !selectedFile) return;
    
    // Add user message
    const newUserMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      sender: 'user'
    };
    
    setMessages(prev => [...prev, newUserMessage]);
    setInputText('');
    setIsLoading(true);
    
    // Simulate response (for demo)
    setTimeout(() => {
      const demoResponses = [
        "Voici les informations que j'ai trouvées dans la base de connaissances concernant votre question. Les procédures d'onboarding sont disponibles dans le document 'Onboarding_Procedures.pdf' sur le SharePoint de l'entreprise.",
        "D'après la documentation technique, la pièce que vous montrez sur l'image est une valve de régulation modèle TR-7500. Vous trouverez le guide de maintenance dans la section 'Équipements industriels' du portail technique.",
        "Pour résoudre ce problème de connexion, veuillez vérifier que votre VPN est actif et que vous utilisez les identifiants du domaine principal. Si le problème persiste, contactez le support IT au poste 4500.",
        "J'ai trouvé plusieurs documents pertinents concernant votre demande. Le plus récent est la note de service du 15 mars concernant les nouvelles procédures de demande de congés. Souhaitez-vous que je vous en fournisse un résumé?"
      ];
      
      const useCases = ['employee_assistance', 'knowledge_management', 'maintenance', 'helpdesk'];
      
      const newBotMessage: Message = {
        id: Date.now().toString(),
        text: demoResponses[Math.floor(Math.random() * demoResponses.length)],
        sender: 'bot',
        useCase: useCases[Math.floor(Math.random() * useCases.length)]
      };
      
      setMessages(prev => [...prev, newBotMessage]);
      setIsLoading(false);
      setSelectedFile(null);
    }, 1500);
  };
  
  // Reset conversation
  const resetConversation = () => {
    setMessages([
      {
        id: '1',
        text: "Bonjour ! Je suis votre assistant d'entreprise multimodal. Je peux vous aider avec :\n- Assistance aux employés (RH, IT, logistique)\n- Recherche documentaire et gestion des connaissances\n- Maintenance et diagnostic technique\n- Support informatique interne\n\nVous pouvez également m'envoyer des images, des fichiers audio ou vidéo pour une assistance plus précise.",
        sender: 'bot'
      }
    ]);
    setSelectedFile(null);
  };
  
  // Get use case label
  const getUseCaseLabel = (useCase: string) => {
    switch(useCase) {
      case 'employee_assistance': return 'RH';
      case 'knowledge_management': return 'Documentation';
      case 'maintenance': return 'Maintenance';
      case 'helpdesk': return 'IT Support';
      case 'multimodal': return 'Multimodal';
      default: return 'Général';
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
          <h1 className="text-xl font-semibold">Assistant d'Entreprise Multimodal</h1>
          <button 
            onClick={resetConversation}
            className="px-3 py-1 text-sm bg-transparent border border-white rounded-md hover:bg-blue-700 transition"
          >
            Nouvelle conversation
          </button>
        </div>
        
        {/* Messages */}
        <div className="bg-white border-l border-r border-gray-200 h-[60vh] overflow-y-auto p-4">
          {messages.map((message) => (
            <div 
              key={message.id} 
              className={`mb-4 max-w-[80%] ${
                message.sender === 'user' 
                  ? 'ml-auto bg-gray-100 rounded-lg p-3 text-right' 
                  : 'mr-auto bg-blue-50 rounded-lg p-3'
              }`}
            >
              <div className="whitespace-pre-line">{message.text}</div>
              
              {message.fileUrl && message.fileType === 'image' && (
                <img src={message.fileUrl} alt="Attached" className="mt-2 max-w-full max-h-40 rounded-md" />
              )}
              
              {message.fileUrl && message.fileType === 'audio' && (
                <audio src={message.fileUrl} controls className="mt-2 max-w-full" />
              )}
              
              {message.fileUrl && message.fileType === 'video' && (
                <video src={message.fileUrl} controls className="mt-2 max-w-full max-h-40" />
              )}
              
              {message.sender === 'bot' && message.useCase && (
                <span className="inline-block mt-2 px-2 py-1 text-xs bg-gray-200 text-gray-700 rounded-full">
                  {getUseCaseLabel(message.useCase)}
                </span>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        
        {/* File Upload */}
        <div className="bg-gray-50 border-l border-r border-gray-200 p-4">
          <div className="flex items-center">
            <label className="block w-full">
              <span className="text-gray-700 text-sm">Joindre un fichier (optionnel)</span>
              <input 
                type="file" 
                className="mt-1 block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100"
                onChange={handleFileChange}
                accept=".jpg,.jpeg,.png,.gif,.pdf,.docx,.pptx,.xlsx,.mp3,.wav,.mp4,.avi"
              />
            </label>
          </div>
          
          <FilePreview file={selectedFile} onClear={clearSelectedFile} />
        </div>
        
        {/* Input */}
        <div className="bg-gray-100 border border-gray-200 p-4 rounded-b-lg flex">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Tapez votre message ici..."
            className="flex-grow px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading}
            className="ml-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-blue-300"
          >
            Envoyer
          </button>
        </div>
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="text-center mt-4">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"></div>
            <p className="mt-2 text-gray-600">Traitement en cours...</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
