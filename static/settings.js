// Settings page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const settingsForm = document.getElementById('settings-form');
    const resetDefaultsBtn = document.getElementById('reset-defaults');
    const temperatureSlider = document.getElementById('temperature');
    const temperatureValue = document.getElementById('temperature-value');
    const settingsStatus = document.getElementById('settings-status');
    const serverStatus = document.getElementById('server-status');
    const connectedModel = document.getElementById('connected-model');
    const dbSize = document.getElementById('db-size');
    const availableModels = document.getElementById('available-models');
    
    // Default settings
    const defaultSettings = {
        ollama_base_url: 'http://192.168.21.237:11434/',
        ollama_model: 'command-r7b-arabic',
        temperature: '0.1',
        chroma_persist_dir: './chroma_db',
        max_context: '120',
        default_language: 'auto'
    };
    
    // Update temperature value display when slider changes
    temperatureSlider.addEventListener('input', function() {
        temperatureValue.textContent = this.value;
    });
    
    // Load available models and populate select  
    function loadModels() {
        return fetch('/api/models')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to load models');
                }
                return response.json();
            })
            .then(data => {
                const select = document.getElementById('ollama_model');
                select.innerHTML = ''; // Clear existing options
                if (data.models && Array.isArray(data.models)) {
                    // Store current selected model value
                    const currentModel = select.value;
                    let firstModel = null;
                    
                    data.models.forEach((model, index) => {
                        const option = document.createElement('option');
                        option.value = model;
                        option.textContent = model;
                        select.appendChild(option);
                        
                        // Track the first model
                        if (index === 0) {
                            firstModel = model;
                        }
                    });
                      // Always select the first model by default
                    if (firstModel) {
                        select.value = firstModel;
                    }
                }
                return data;
            })
            .catch(error => {
                console.error('Error loading models:', error);
                const select = document.getElementById('ollama_model');
                select.innerHTML = '<option value="">Error loading models</option>';
            });
    }
    
    // Load current settings
    function loadSettings() {
        // First load available models
        return loadModels()
            .then(() => {
                // Then fetch current config
                return fetch('/api/config');
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to load settings');
                }
                return response.json();
            })
            .then(data => {
                // Fill form with current settings
                document.getElementById('ollama_base_url').value = data.ollama_base_url || defaultSettings.ollama_base_url;
                document.getElementById('ollama_model').value = data.ollama_model || defaultSettings.ollama_model;
                document.getElementById('temperature').value = data.temperature || defaultSettings.temperature;
                temperatureValue.textContent = data.temperature || defaultSettings.temperature;
                document.getElementById('chroma_persist_dir').value = data.chroma_persist_dir || defaultSettings.chroma_persist_dir;
                document.getElementById('max_context').value = data.max_context || defaultSettings.max_context;
                document.getElementById('default_language').value = data.default_language || defaultSettings.default_language;
            })
            .catch(error => {
                console.error('Error loading settings:', error);
                showStatusMessage('Error loading settings: ' + error.message, 'error');
            });
    }
    
    // Save settings
    settingsForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = {
            ollama_base_url: document.getElementById('ollama_base_url').value,
            ollama_model: document.getElementById('ollama_model').value,
            temperature: document.getElementById('temperature').value,
            chroma_persist_dir: document.getElementById('chroma_persist_dir').value,
            max_context: document.getElementById('max_context').value,
            default_language: document.getElementById('default_language').value
        };
        
        fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to save settings');
            }
            return response.json();
        })
        .then(data => {
            showStatusMessage('Settings saved successfully', 'success');
            // Reload system info
            loadSystemInfo();
        })
        .catch(error => {
            console.error('Error saving settings:', error);
            showStatusMessage('Error saving settings: ' + error.message, 'error');
        });
    });
    
    // Reset to defaults
    resetDefaultsBtn.addEventListener('click', function() {
        // Fill form with default settings
        document.getElementById('ollama_base_url').value = defaultSettings.ollama_base_url;
        document.getElementById('ollama_model').value = defaultSettings.ollama_model;
        document.getElementById('temperature').value = defaultSettings.temperature;
        temperatureValue.textContent = defaultSettings.temperature;
        document.getElementById('chroma_persist_dir').value = defaultSettings.chroma_persist_dir;
        document.getElementById('max_context').value = defaultSettings.max_context;
        document.getElementById('default_language').value = defaultSettings.default_language;
        
        showStatusMessage('Default settings restored. Click Save to apply.', 'success');
    });
    
    // Show status message
    function showStatusMessage(message, type) {
        settingsStatus.textContent = message;
        settingsStatus.className = 'status-message ' + type;
        
        // Hide message after 5 seconds
        setTimeout(function() {
            settingsStatus.style.display = 'none';
        }, 5000);
    }
    
    // Load system information
    function loadSystemInfo() {
        // Check server status
        fetch('/api/health')
            .then(response => {
                if (response.ok) {
                    serverStatus.textContent = 'Online';
                    serverStatus.classList.add('online');
                    return response.json();
                } else {
                    throw new Error('Server offline');
                }
            })
            .then(data => {
                // Update connected model
                if (data.model) {
                    connectedModel.textContent = data.model;
                }
                
                // Get database info
                return fetch('/api/documents/stats');
            })
            .then(response => response.json())
            .then(data => {
                // Update database size
                if (data.document_count !== undefined) {
                    dbSize.textContent = `${data.document_count} documents, ${formatBytes(data.storage_size || 0)}`;
                }
                
            // Get available models
                return fetch('/api/models');
            })
            .then(response => response.json())
            .then(data => {
                // Update available models list
                if (data.models) {
                    availableModels.textContent = data.models.join(', ');
                }
            })
            .catch(error => {
                console.error('Error loading system info:', error);
                if (error.message === 'Server offline') {
                    serverStatus.textContent = 'Offline';
                    serverStatus.classList.add('offline');
                    connectedModel.textContent = 'N/A';
                    dbSize.textContent = 'N/A';
                    availableModels.textContent = 'N/A';
                }
            });
    }
    
    // Format bytes to human-readable size
    function formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }
    
    // Initial load
    loadSettings();
    loadSystemInfo();
});
