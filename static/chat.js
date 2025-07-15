// Fixed Chat functionality - working version
console.log('External JavaScript loaded (fixed version)');

// Global variables
let messageCount = 0;

// Send message function with AOS integration
async function sendMessage() {
    console.log('Send function called (AOS enhanced)');
    const input = document.getElementById('chat-input');
    const phoneInput = document.getElementById('phone-number');
    const nameInput = document.getElementById('customer-name-form');
    const message = input.value.trim();
    
    if (!message) {
        alert('Please enter a message');
        return;
    }
    
    // Add user message
    addMessage(message, 'user');
    input.value = '';
    updateCharCount();
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send to AOS API
    try {
        const requestData = {
            query: message,
            phone_number: phoneInput ? phoneInput.value.trim() : '',
            first_name: nameInput ? nameInput.value.trim() : ''
        };
        
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        console.log('AOS API Response:', data);
        hideTypingIndicator();
        
        if (data.success) {
            console.log('Adding assistant message:', data.response);
            addMessage(data.response, 'assistant');
            
            // Handle tool calls
            if (data.tool_calls && data.tool_calls.length > 0) {
                console.log('Tools used:', data.tool_calls.map(tc => tc.tool));
                
                // Handle search_products tool call
                const searchResult = data.tool_calls.find(tc => tc.tool === 'search_products');
                if (searchResult && searchResult.result && searchResult.result.products) {
                    displaySearchResults(searchResult.result.products);
                }
                
                // Handle appointment tool calls
                const frustrationResult = data.tool_calls.find(tc => tc.tool === 'detect_customer_frustration');
                if (frustrationResult && frustrationResult.result && frustrationResult.result.should_offer_appointment) {
                    showAppointmentSuggestion(frustrationResult.result);
                }
                
                const appointmentResult = data.tool_calls.find(tc => tc.tool === 'get_available_appointments');
                if (appointmentResult && appointmentResult.result && appointmentResult.result.success) {
                    showAppointmentOptions(appointmentResult.result);
                }
                
                const scheduleResult = data.tool_calls.find(tc => tc.tool === 'schedule_appointment');
                if (scheduleResult && scheduleResult.result && scheduleResult.result.success) {
                    showAppointmentConfirmation(scheduleResult.result);
                }
                
                // Show AOS phase if available from tools
                const aosResult = data.tool_calls.find(tc => tc.tool === 'get_aos_questions');
                if (aosResult && aosResult.result && aosResult.result.current_phase) {
                    showAOSPhase(aosResult.result.current_phase);
                }
            }
            
        } else {
            console.log('Adding error message:', data.error);
            addMessage('Error: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Send error:', error);
        hideTypingIndicator();
        addMessage('Connection error: ' + error.message, 'error');
    }
}

// Load RAG status and record count
async function loadRAGStatus() {
    try {
        const response = await fetch('/api/database/stats');
        const data = await response.json();
        
        if (data.success && data.stats) {
            const recordCount = data.stats.total_products || 0;
            const recordsCountEl = document.getElementById('records-count');
            const footerProductCountEl = document.getElementById('footer-product-count');
            
            if (recordsCountEl) {
                recordsCountEl.textContent = recordCount.toLocaleString();
            }
            if (footerProductCountEl) {
                footerProductCountEl.textContent = recordCount.toLocaleString();
            }
        }
        
        // Load and display last sync timestamp from localStorage
        loadLastSyncTime();
        
    } catch (error) {
        console.error('Error loading RAG status:', error);
        const recordsCountEl = document.getElementById('records-count');
        if (recordsCountEl) {
            recordsCountEl.textContent = 'Error loading';
        }
    }
}

// Load last sync timestamp from localStorage
function loadLastSyncTime() {
    const lastSyncTime = localStorage.getItem('lastSyncTime');
    const lastSyncEl = document.getElementById('last-sync-time');
    const footerLastSyncEl = document.getElementById('footer-last-sync-time');
    
    if (lastSyncTime) {
        const syncDate = new Date(lastSyncTime);
        const timeStr = syncDate.toLocaleString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        if (lastSyncEl) {
            lastSyncEl.textContent = `Last sync: ${timeStr}`;
        }
        if (footerLastSyncEl) {
            footerLastSyncEl.textContent = timeStr;
        }
    } else {
        if (lastSyncEl) {
            lastSyncEl.textContent = 'No sync yet';
        }
        if (footerLastSyncEl) {
            footerLastSyncEl.textContent = 'Never';
        }
    }
}

// Save sync timestamp to localStorage
function saveLastSyncTime() {
    const now = new Date().toISOString();
    localStorage.setItem('lastSyncTime', now);
}

// Sync function
async function syncData() {
    console.log('Sync function called (external)');
    const btn = document.getElementById('sync-data-button');
    const syncMessage = document.getElementById('sync-status-message');
    const lastSyncEl = document.getElementById('last-sync-time');
    const recordsCountEl = document.getElementById('records-count');
    if (!btn) return;
    
    // Capture current record count before sync
    const currentCount = recordsCountEl ? recordsCountEl.textContent : '0';
    
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="material-icons mr-2">sync</span> Syncing...';
    btn.disabled = true;
    
    // Show current count in sync message
    if (syncMessage) {
        syncMessage.textContent = `Syncing... Current records: ${currentCount}`;
    }
    
    try {
        const response = await fetch('/api/rag/sync', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            btn.innerHTML = '<span class="material-icons mr-2">check_circle</span> Synced!';
            
            // Save sync timestamp to localStorage
            saveLastSyncTime();
            
            // Get updated record count
            await loadRAGStatus();
            
            // Get the new record count after sync
            const newCount = recordsCountEl ? recordsCountEl.textContent : '0';
            
            // Update sync timestamp display
            const now = new Date();
            const timeStr = now.toLocaleString('en-US', { 
                month: 'short', 
                day: 'numeric', 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            
            if (lastSyncEl) {
                lastSyncEl.textContent = `Last sync: ${timeStr}`;
            }
            
            if (syncMessage) {
                syncMessage.textContent = `Sync completed: ${currentCount} → ${newCount} records`;
            }
            
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
                if (syncMessage) syncMessage.textContent = '';
            }, 3000);
        } else {
            btn.innerHTML = '<span class="material-icons mr-2">error</span> Failed';
            if (syncMessage) {
                syncMessage.textContent = `Sync failed: ${data.error || 'Unknown error'} (${currentCount} records unchanged)`;
            }
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
                if (syncMessage) syncMessage.textContent = '';
            }, 3000);
        }
    } catch (error) {
        console.error('Sync error:', error);
        btn.innerHTML = '<span class="material-icons mr-2">error</span> Failed';
        if (syncMessage) {
            syncMessage.textContent = `Connection error (${currentCount} records unchanged)`;
        }
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
            if (syncMessage) syncMessage.textContent = '';
        }, 3000);
    }
}

// Clear chat function
function clearChat() {
    console.log('Clear function called (external)');
    const container = document.getElementById('chat-messages');
    if (!container) return;
    
    container.innerHTML = `
        <div class="flex justify-start">
            <div class="message-bubble assistant">
                <p>Hi! I'm Alex, your tile specialist. What project are you working on?</p>
                <p class="message-timestamp">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
            </div>
        </div>
    `;
    messageCount = 0;
    const messageCountEl = document.getElementById('message-count');
    if (messageCountEl) messageCountEl.textContent = messageCount;
}

// Export function
function exportResults() {
    console.log('Export function called (external)');
    if (messageCount === 0) {
        return; // No data to export, but don't show popup
    }

    const dataToExport = {
        chatHistory: Array.from(document.querySelectorAll('.message-bubble')).map(bubble => ({
            type: bubble.classList.contains('user') ? 'user' : 'assistant',
            content: bubble.querySelector('p').textContent,
            timestamp: new Date().toISOString()
        })),
        timestamp: new Date().toISOString()
    };

    const jsonString = JSON.stringify(dataToExport, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat_export_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Refresh function
function refreshData() {
    console.log('Refresh function called (external)');
    location.reload(); // Refresh without confirmation popup
}

// Display search results
function displaySearchResults(products) {
    console.log('Displaying search results:', products);
    const container = document.getElementById('chat-messages');
    if (!container) return;
    
    if (!products || products.length === 0) {
        return;
    }
    
    const resultsDiv = document.createElement('div');
    resultsDiv.className = 'flex justify-start mb-4';
    
    let resultsHTML = `
        <div class="message-bubble assistant">
            <div class="search-results">
                <h4 class="font-semibold text-gray-800 mb-3">🔍 Search Results</h4>
                <div class="grid gap-3">
    `;
    
    products.forEach(product => {
        const imageUrl = product.primary_image || '/static/placeholder-tile.jpg';
        const price = product.price_per_sqft ? `$${product.price_per_sqft}/sq ft` : 'Price available in store';
        
        resultsHTML += `
            <div class="product-card bg-white border rounded-lg p-3 hover:shadow-md transition-shadow">
                <div class="flex gap-3">
                    <img src="${imageUrl}" alt="${product.title}" class="w-16 h-16 object-cover rounded" onerror="this.src='/static/placeholder-tile.jpg'">
                    <div class="flex-1">
                        <h5 class="font-medium text-sm text-gray-800">${product.title}</h5>
                        <p class="text-xs text-gray-600 mt-1">SKU: ${product.sku}</p>
                        <p class="text-sm font-semibold text-blue-600 mt-1">${price}</p>
                        ${product.size_shape ? `<p class="text-xs text-gray-500">Size: ${product.size_shape}</p>` : ''}
                        ${product.color ? `<p class="text-xs text-gray-500">Color: ${product.color}</p>` : ''}
                    </div>
                </div>
            </div>
        `;
    });
    
    resultsHTML += `
                </div>
            </div>
            <p class="message-timestamp">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
        </div>
    `;
    
    resultsDiv.innerHTML = resultsHTML;
    container.appendChild(resultsDiv);
    container.scrollTop = container.scrollHeight;
}

// Add message to chat
function addMessage(text, type) {
    console.log('addMessage called with:', text, type);
    const container = document.getElementById('chat-messages');
    
    if (!container) {
        console.error('Chat messages container not found!');
        return;
    }
    
    const div = document.createElement('div');
    div.className = 'flex';
    
    // Convert markdown to HTML for assistant messages
    let processedText = text;
    if (type === 'assistant') {
        processedText = convertMarkdownToHtml(text);
    }
    
    if (type === 'user') {
        div.className += ' justify-end';
        div.innerHTML = `
            <div class="message-bubble user">
                <p>${text}</p>
                <small class="text-blue-100 text-xs">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</small>
            </div>
        `;
    } else {
        div.innerHTML = `
            <div class="message-bubble assistant">
                <div>${processedText}</div>
                <small class="text-gray-500 text-xs">${type === 'error' ? 'Error' : 'Assistant'} - ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</small>
            </div>
        `;
    }
    
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    
    messageCount++;
    const messageCountEl = document.getElementById('message-count');
    if (messageCountEl) {
        messageCountEl.textContent = messageCount;
    }
    
    console.log('Message added successfully, total messages:', messageCount);
}

// Convert markdown to HTML
function convertMarkdownToHtml(text) {
    // Convert markdown images: ![alt text](url) to <img> tags
    text = text.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" style="max-width: 200px; height: auto; border-radius: 8px; margin: 8px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />');
    
    // Convert markdown links: [text](url) to <a> tags
    text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" style="color: #3b82f6; text-decoration: underline;">$1</a>');
    
    // Convert **bold** text
    text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Convert line breaks to <br> tags
    text = text.replace(/\n/g, '<br>');
    
    // Format product entries with better structure
    text = text.replace(/(\d+\.\s\*\*[^*]+\*\*)/g, '<div style="margin: 12px 0; padding: 8px; background: #f8f9fa; border-radius: 6px; border-left: 3px solid #3b82f6;">$1</div>');
    
    return text;
}

// Update character count
function updateCharCount() {
    const input = document.getElementById('chat-input');
    const count = document.getElementById('char-count');
    if (count && input) count.textContent = `${input.value.length}/200`;
}

// Use suggestion
function useSuggestion(text) {
    console.log('Suggestion clicked:', text);
    const input = document.getElementById('chat-input');
    if (input) {
        input.value = text;
        updateCharCount();
        sendMessage();
    }
}

// AOS Helper Functions
function showTypingIndicator() {
    const container = document.getElementById('typing-indicator-container');
    if (container) {
        container.classList.remove('hidden');
    }
}

function hideTypingIndicator() {
    const container = document.getElementById('typing-indicator-container');
    if (container) {
        container.classList.add('hidden');
    }
}

function showAOSPhase(phase) {
    // Create or update AOS phase indicator
    let phaseIndicator = document.getElementById('aos-phase-indicator');
    if (!phaseIndicator) {
        phaseIndicator = document.createElement('div');
        phaseIndicator.id = 'aos-phase-indicator';
        phaseIndicator.className = 'fixed top-20 right-4 bg-blue-500 text-white px-3 py-1 rounded-lg text-sm z-50';
        document.body.appendChild(phaseIndicator);
    }
    
    const phaseNames = {
        'greeting': '👋 Greeting',
        'needs_assessment': '📋 Needs Assessment',
        'design_details': '🎨 Design Consultation',
        'close': '🤝 Closing',
        'objection_handling': '💬 Objection Handling'
    };
    
    phaseIndicator.textContent = phaseNames[phase] || `📊 ${phase}`;
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        if (phaseIndicator) {
            phaseIndicator.style.opacity = '0.5';
        }
    }, 3000);
}

function showCollectedInfo(collectedInfo) {
    // Create or update collected info panel
    let infoPanel = document.getElementById('collected-info-panel');
    if (!infoPanel) {
        infoPanel = document.createElement('div');
        infoPanel.id = 'collected-info-panel';
        infoPanel.className = 'fixed bottom-20 right-4 bg-green-50 border border-green-200 rounded-lg p-3 max-w-sm text-sm z-50';
        document.body.appendChild(infoPanel);
    }
    
    const infoKeys = Object.keys(collectedInfo);
    if (infoKeys.length === 0) {
        infoPanel.style.display = 'none';
        return;
    }
    
    let infoHTML = '<div class="font-semibold text-green-800 mb-2">📊 Project Information</div>';
    
    if (collectedInfo.project_type) {
        infoHTML += `<div>🏠 <strong>Project:</strong> ${collectedInfo.project_type}</div>`;
    }
    if (collectedInfo.surface_area_sf) {
        infoHTML += `<div>📐 <strong>Area:</strong> ${collectedInfo.surface_area_sf} sq ft</div>`;
    }
    if (collectedInfo.installation_method) {
        infoHTML += `<div>🔧 <strong>Installation:</strong> ${collectedInfo.installation_method}</div>`;
    }
    if (collectedInfo.budget_range) {
        infoHTML += `<div>💰 <strong>Budget:</strong> ${collectedInfo.budget_range}</div>`;
    }
    if (collectedInfo.project_timeline) {
        infoHTML += `<div>📅 <strong>Timeline:</strong> ${collectedInfo.project_timeline}</div>`;
    }
    
    const completionPercentage = Math.round((infoKeys.length / 6) * 100); // 6 key fields
    infoHTML += `<div class="mt-2 pt-2 border-t border-green-200 text-xs text-green-600">Progress: ${completionPercentage}%</div>`;
    
    infoPanel.innerHTML = infoHTML;
    infoPanel.style.display = 'block';
}

// DOM Ready initialization
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded - External JavaScript initializing...');
    
    // Load RAG status on page load
    loadRAGStatus();
    
    // Add chat input listeners
    const input = document.getElementById('chat-input');
    if (input) {
        input.addEventListener('input', updateCharCount);
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        input.focus();
        console.log('Chat input listeners added');
    }

    // Add button onclick handlers directly
    const syncBtn = document.getElementById('sync-data-button');
    const clearBtn = document.getElementById('clear-chat-button');
    const exportBtn = document.getElementById('export-results-button');
    const refreshBtn = document.getElementById('refresh-data-button');
    const sendBtn = document.getElementById('send-button');
    
    if (syncBtn) syncBtn.onclick = syncData;
    if (clearBtn) clearBtn.onclick = clearChat;
    if (exportBtn) exportBtn.onclick = exportResults;
    if (refreshBtn) refreshBtn.onclick = refreshData;
    if (sendBtn) sendBtn.onclick = sendMessage;

    // Add suggestion button listeners
    document.querySelectorAll('.suggestion-chip').forEach((button, index) => {
        button.onclick = function() {
            console.log(`Suggestion ${index} clicked:`, this.textContent);
            useSuggestion(this.textContent);
        };
    });
    console.log('Suggestion chip onclick assigned:', document.querySelectorAll('.suggestion-chip').length);
    
    // Set welcome timestamp
    const welcomeTimestamp = document.getElementById('welcome-timestamp');
    if (welcomeTimestamp) {
        welcomeTimestamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    // Test that container exists
    const testContainer = document.getElementById('chat-messages');
    console.log('Chat messages container found:', !!testContainer);
    
    // Initialize form system
    initializeFormSystem();
    if (testContainer) {
        console.log('Container element:', testContainer);
    }
    
    // Initialize the dynamic form system
    initializeFormSystem();
    
    console.log('✅ External JavaScript initialization complete!');
});

// ========================================
// DYNAMIC FORM SYSTEM FUNCTIONS
// ========================================

// Global form data storage
let projectData = {
    customer: {},
    project: {},
    areas: {},
    surfaces: [],
    currentSurface: {}
};

// Toggle form panel
function toggleFormPanel() {
    const panel = document.getElementById('form-panel');
    const toggle = document.getElementById('form-toggle');
    
    if (panel.classList.contains('open')) {
        panel.classList.remove('open');
        toggle.innerHTML = '<i class="fas fa-clipboard-list"></i>';
    } else {
        panel.classList.add('open');
        toggle.innerHTML = '<i class="fas fa-times"></i>';
        // Trigger form opened event for chat integration
        notifyFormOpened();
    }
}

// Notify chat system that form was opened
function notifyFormOpened() {
    // Send structured context update to chat
    sendStructuredContextUpdate('opened_panel', projectData);
}

// Customer lookup function
async function lookupCustomer() {
    const phoneInput = document.getElementById('customer-phone');
    const phone = phoneInput.value.trim();
    
    if (!phone) {
        alert('Please enter a phone number');
        return;
    }
    
    const statusDiv = document.getElementById('phone-status');
    const statusText = document.getElementById('phone-status-text');
    const differentBtn = document.getElementById('different-number-btn');
    
    statusDiv.style.display = 'block';
    statusText.textContent = 'Searching...';
    statusDiv.className = 'phone-status';
    
    try {
        // Check if customer exists in database
        const response = await fetch(`/api/customers/lookup/${phone}`);
        const data = await response.json();
        
        if (data.success && data.customer) {
            // Customer found
            statusDiv.className = 'phone-status found';
            statusText.textContent = `✅ Found: ${data.customer.name}`;
            differentBtn.style.display = 'inline-block';
            
            // Populate customer data
            document.getElementById('customer-name').value = data.customer.name || '';
            document.getElementById('customer-email').value = data.customer.email || '';
            
            // Store customer data
            projectData.customer = data.customer;
            
            // Show existing projects if any
            if (data.projects && data.projects.length > 0) {
                const continueOption = document.getElementById('continue-project-option');
                const projectSelect = document.getElementById('existing-projects');
                
                continueOption.style.display = 'block';
                projectSelect.innerHTML = '<option value="">Select existing project...</option>';
                
                data.projects.forEach(project => {
                    const option = document.createElement('option');
                    option.value = project.id;
                    option.textContent = `${project.name} - ${project.address}`;
                    projectSelect.appendChild(option);
                });
            }
            
            // Auto-save customer data
            autoSaveProject();
            
        } else {
            // Customer not found
            statusDiv.className = 'phone-status not-found';
            statusText.textContent = '❌ Not found - New customer setup';
            differentBtn.style.display = 'inline-block';
            
            // Clear fields for new customer
            document.getElementById('customer-name').value = '';
            document.getElementById('customer-email').value = '';
            
            // Focus on name field
            document.getElementById('customer-name').focus();
        }
        
    } catch (error) {
        console.error('Error looking up customer:', error);
        statusDiv.className = 'phone-status not-found';
        statusText.textContent = '❌ Error searching - Please try again';
    }
}

// Enter different number
function enterDifferentNumber() {
    const phoneInput = document.getElementById('customer-phone');
    const statusDiv = document.getElementById('phone-status');
    
    phoneInput.value = '';
    phoneInput.focus();
    statusDiv.style.display = 'none';
    
    // Clear customer data
    document.getElementById('customer-name').value = '';
    document.getElementById('customer-email').value = '';
    document.getElementById('continue-project-option').style.display = 'none';
    
    projectData.customer = {};
}

// Update current selection
function updateCurrentSelection() {
    const area = document.getElementById('area-select').value;
    const surface = document.getElementById('surface-select').value;
    
    if (area && surface) {
        projectData.currentSurface = {
            area: area,
            surface: surface,
            dimensions: {}
        };
        
        // Update measurement type based on surface
        updateMeasurementType(surface);
        
        // Calculate current surface
        calculateSurface();
        
        // Auto-save
        autoSaveProject();
    }
}

// Update measurement type based on surface
function updateMeasurementType(surface) {
    const linearSurfaces = ['niche-trim', 'wall-framing-trim', 'curb', 'threshold', 'floor-molding'];
    const unit = document.getElementById('calculated-unit');
    
    if (linearSurfaces.includes(surface)) {
        unit.textContent = 'linear ft';
        document.getElementById('surface-width').style.display = 'none';
        document.getElementById('surface-height').style.display = 'none';
    } else {
        unit.textContent = 'sq ft';
        document.getElementById('surface-width').style.display = 'block';
        document.getElementById('surface-height').style.display = 'block';
    }
}

// Calculate surface area/linear feet
function calculateSurface() {
    const length = parseFloat(document.getElementById('surface-length').value) || 0;
    const width = parseFloat(document.getElementById('surface-width').value) || 0;
    const height = parseFloat(document.getElementById('surface-height').value) || 0;
    const surface = document.getElementById('surface-select').value;
    
    const linearSurfaces = ['niche-trim', 'wall-framing-trim', 'curb', 'threshold', 'floor-molding'];
    
    let calculated = 0;
    
    if (linearSurfaces.includes(surface)) {
        // Linear measurement
        calculated = length;
    } else {
        // Square footage calculation
        if (surface === 'wall' || surface === 'half-wall' || surface === 'wainscoting') {
            calculated = length * height;
        } else {
            calculated = length * width;
        }
    }
    
    document.getElementById('calculated-value').textContent = calculated.toFixed(1);
    
    // Store in current surface data
    if (projectData.currentSurface) {
        projectData.currentSurface.dimensions = {
            length: length,
            width: width,
            height: height,
            calculated: calculated
        };
    }
    
    // Update materials calculation
    updateMaterialsCalculation();
    
    // Auto-save
    autoSaveProject();
    
    // Notify chat about dimensions
    if (calculated > 0) {
        sendStructuredContextUpdate('dimensions_entered', projectData);
    }
}

// Update materials calculation
function updateMaterialsCalculation() {
    const calculated = parseFloat(document.getElementById('calculated-value').textContent) || 0;
    const selectedTile = projectData.currentSurface?.selectedTile;
    
    if (!selectedTile || calculated === 0) {
        document.getElementById('grout-recommendation').textContent = 'Select tile first';
        document.getElementById('total-cost').textContent = '$0.00';
        return;
    }
    
    // Calculate grout recommendation
    const groutRec = calculateGroutRecommendation(selectedTile, calculated);
    document.getElementById('grout-recommendation').textContent = groutRec.text;
    
    // Calculate total cost
    const tileCost = calculated * (selectedTile.price || 0);
    const groutCost = groutRec.cost || 0;
    const totalCost = tileCost + groutCost;
    
    document.getElementById('total-cost').textContent = `$${totalCost.toFixed(2)}`;
}

// Calculate grout recommendation based on tile and area
function calculateGroutRecommendation(tile, sqft) {
    // Simplified grout calculation based on the plan
    const groutType = determineGroutType(tile);
    const groutLbs = calculateGroutQuantity(sqft, tile.size || '12x12');
    const bagRec = recommendGroutBag(groutLbs, groutType);
    
    return {
        text: `${groutType} - ${bagRec.size}lb bag (${bagRec.waste}% waste)`,
        cost: bagRec.price || 18.99
    };
}

// Determine grout type based on tile
function determineGroutType(tile) {
    const materialType = tile.material_type || tile.material || 'ceramic';
    const finish = tile.finish || '';
    
    if (materialType.toLowerCase().includes('marble') || 
        materialType.toLowerCase().includes('travertine') || 
        materialType.toLowerCase().includes('limestone')) {
        
        if (finish.toLowerCase().includes('polished')) {
            return 'Excel Unsanded';
        } else {
            return 'Excel Sanded';
        }
    }
    
    if (tile.edge_type === 'Rectified') {
        return 'Excel Unsanded';
    }
    
    return 'Excel Sanded';
}

// Calculate grout quantity
function calculateGroutQuantity(sqft, tileSize) {
    // Simplified calculation - would use actual grout calculator in production
    const baseRate = 0.067; // lbs per sq ft for typical 12x12 tile
    return Math.ceil(sqft * baseRate);
}

// Recommend grout bag size
function recommendGroutBag(lbs, groutType) {
    if (groutType.includes('Unsanded')) {
        if (lbs <= 5) return { size: 5, waste: Math.round(((5 - lbs) / 5) * 100), price: 12.99 };
        if (lbs <= 20) return { size: 20, waste: Math.round(((20 - lbs) / 20) * 100), price: 35.99 };
        return { size: 25, waste: Math.round(((25 - lbs) / 25) * 100), price: 45.99 };
    } else {
        if (lbs <= 8) return { size: 8, waste: Math.round(((8 - lbs) / 8) * 100), price: 18.99 };
        return { size: 25, waste: Math.round(((25 - lbs) / 25) * 100), price: 45.99 };
    }
}

// Change tile selection
function changeTile() {
    addMessage("I'd like to change the tile selection for this surface", 'user');
    sendMessage();
}

// Add surface to saved list
function addSurface() {
    const area = document.getElementById('area-select').value;
    const surface = document.getElementById('surface-select').value;
    const calculated = parseFloat(document.getElementById('calculated-value').textContent) || 0;
    
    if (!area || !surface || calculated === 0) {
        alert('Please complete all fields before adding the surface');
        return;
    }
    
    const surfaceData = {
        id: Date.now(),
        area: area,
        surface: surface,
        dimensions: projectData.currentSurface.dimensions,
        selectedTile: projectData.currentSurface.selectedTile,
        calculated: calculated
    };
    
    projectData.surfaces.push(surfaceData);
    
    // Update saved surfaces display
    updateSavedSurfacesDisplay();
    
    // Clear current selection
    clearCurrentSelection();
    
    // Auto-save
    autoSaveProject();
    
    // Notify chat
    sendStructuredContextUpdate('surface_added', projectData);
}

// Update saved surfaces display
function updateSavedSurfacesDisplay() {
    const section = document.getElementById('saved-surfaces-section');
    const list = document.getElementById('saved-surfaces-list');
    
    if (projectData.surfaces.length === 0) {
        section.style.display = 'none';
        return;
    }
    
    section.style.display = 'block';
    list.innerHTML = '';
    
    projectData.surfaces.forEach(surface => {
        const item = document.createElement('div');
        item.className = 'bg-gray-50 p-3 rounded-lg mb-2 flex justify-between items-center';
        item.innerHTML = `
            <div>
                <strong>${surface.area} - ${surface.surface}</strong><br>
                <span class="text-sm text-gray-600">${surface.calculated.toFixed(1)} sq ft</span>
                ${surface.selectedTile ? `<br><span class="text-sm text-blue-600">${surface.selectedTile.name}</span>` : ''}
            </div>
            <button onclick="removeSurface(${surface.id})" class="text-red-500 hover:text-red-700">
                <i class="fas fa-trash"></i>
            </button>
        `;
        list.appendChild(item);
    });
}

// Remove surface from saved list
function removeSurface(surfaceId) {
    projectData.surfaces = projectData.surfaces.filter(s => s.id !== surfaceId);
    updateSavedSurfacesDisplay();
    autoSaveProject();
}

// Clear current selection
function clearCurrentSelection() {
    document.getElementById('area-select').value = '';
    document.getElementById('surface-select').value = '';
    document.getElementById('surface-length').value = '';
    document.getElementById('surface-width').value = '';
    document.getElementById('surface-height').value = '';
    document.getElementById('calculated-value').textContent = '0';
    document.getElementById('selected-tile-display').textContent = 'No Tile Selected';
    document.getElementById('grout-recommendation').textContent = 'Select tile first';
    document.getElementById('total-cost').textContent = '$0.00';
    
    projectData.currentSurface = {};
}

// Auto-save project data
function autoSaveProject() {
    const phone = document.getElementById('customer-phone').value.trim();
    const projectName = document.getElementById('project-name').value.trim();
    const address = document.getElementById('project-address').value.trim();
    
    // Update project data
    projectData.customer = {
        ...projectData.customer,
        phone: phone,
        name: document.getElementById('customer-name').value.trim(),
        email: document.getElementById('customer-email').value.trim()
    };
    
    projectData.project = {
        name: projectName,
        address: address,
        surfaces: projectData.surfaces
    };
    
    // Save to localStorage
    localStorage.setItem('tileshop_project', JSON.stringify(projectData));
    
    // Update auto-save status
    document.getElementById('auto-save-status').textContent = 'Auto-saved at ' + new Date().toLocaleTimeString();
    
    // Send to server (optional)
    if (phone && projectName) {
        saveProjectToServer();
    }
}

// Save project to server
async function saveProjectToServer() {
    try {
        const response = await fetch('/api/project/structured-save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                phone: projectData.customer.phone,
                projectData: projectData
            })
        });
        
        const data = await response.json();
        if (data.success) {
            console.log('Project saved to server:', data.project_id);
        }
    } catch (error) {
        console.error('Error saving project to server:', error);
    }
}

// Send structured context update to chat
async function sendStructuredContextUpdate(action, data) {
    try {
        const response = await fetch('/api/chat/structured-context', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: action,
                projectData: data,
                phone: data.customer?.phone || 'unknown'
            })
        });
        
        const result = await response.json();
        if (result.success && result.llm_response) {
            addMessage(result.llm_response, 'assistant');
        }
    } catch (error) {
        console.error('Error sending structured context:', error);
    }
}

// Load saved project data
function loadSavedProject() {
    const saved = localStorage.getItem('tileshop_project');
    if (saved) {
        try {
            projectData = JSON.parse(saved);
            
            // Populate form fields
            if (projectData.customer) {
                document.getElementById('customer-phone').value = projectData.customer.phone || '';
                document.getElementById('customer-name').value = projectData.customer.name || '';
                document.getElementById('customer-email').value = projectData.customer.email || '';
            }
            
            if (projectData.project) {
                document.getElementById('project-name').value = projectData.project.name || '';
                document.getElementById('project-address').value = projectData.project.address || '';
            }
            
            // Update saved surfaces display
            updateSavedSurfacesDisplay();
            
        } catch (error) {
            console.error('Error loading saved project:', error);
        }
    }
}

// Initialize form system
function initializeFormSystem() {
    // Load saved project data
    loadSavedProject();
    
    // Add event listeners for auto-save
    const formInputs = document.querySelectorAll('#form-panel input, #form-panel select');
    formInputs.forEach(input => {
        input.addEventListener('input', () => {
            setTimeout(autoSaveProject, 500); // Debounced auto-save
        });
        input.addEventListener('change', autoSaveProject);
    });
    
    // Phone number formatting
    const phoneInput = document.getElementById('customer-phone');
    phoneInput.addEventListener('input', formatPhoneNumber);
    
    console.log('Dynamic form system initialized');
}

// Format phone number as user types
function formatPhoneNumber() {
    const input = document.getElementById('customer-phone');
    let value = input.value.replace(/\D/g, ''); // Remove non-digits
    
    if (value.length >= 6) {
        value = value.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
    } else if (value.length >= 3) {
        value = value.replace(/(\d{3})(\d{0,3})/, '($1) $2');
    }
    
    input.value = value;
}

// Phase 4: Appointment System Functions
function showAppointmentSuggestion(frustrationResult) {
    console.log('Showing appointment suggestion:', frustrationResult);
    
    const container = document.getElementById('chat-messages');
    if (!container) return;
    
    const appointmentCard = document.createElement('div');
    appointmentCard.className = 'appointment-suggestion';
    appointmentCard.innerHTML = `
        <div class="appointment-card">
            <div class="appointment-header">
                <i class="fas fa-calendar-plus"></i>
                <h3>Need Extra Help?</h3>
            </div>
            <p>I can sense this might be getting complex. Let me schedule a free consultation where we can walk through everything together!</p>
            <div class="appointment-actions">
                <button class="btn btn-primary" onclick="requestAppointmentOptions()">
                    <i class="fas fa-calendar"></i> See Available Times
                </button>
                <button class="btn btn-secondary" onclick="dismissAppointmentSuggestion(this)">
                    <i class="fas fa-times"></i> Continue Here
                </button>
            </div>
            <div class="frustration-debug" style="font-size: 0.8em; color: #666; margin-top: 10px;">
                Frustration Level: ${frustrationResult.frustration_level} (Score: ${frustrationResult.frustration_score})
            </div>
        </div>
    `;
    
    container.appendChild(appointmentCard);
    container.scrollTop = container.scrollHeight;
}

function showAppointmentOptions(appointmentData) {
    console.log('Showing appointment options:', appointmentData);
    
    const container = document.getElementById('chat-messages');
    if (!container) return;
    
    const optionsCard = document.createElement('div');
    optionsCard.className = 'appointment-options';
    
    let appointmentTypesHTML = '';
    for (const [type, details] of Object.entries(appointmentData.appointment_types)) {
        appointmentTypesHTML += `
            <div class="appointment-type" onclick="selectAppointmentType('${type}')">
                <h4>${details.name}</h4>
                <p>${details.description}</p>
                <span class="appointment-duration">${details.duration} • ${details.cost}</span>
            </div>
        `;
    }
    
    let timeSlotsHTML = '';
    appointmentData.available_slots.forEach(slot => {
        timeSlotsHTML += `
            <button class="time-slot" onclick="selectTimeSlot('${slot}')">${slot}</button>
        `;
    });
    
    optionsCard.innerHTML = `
        <div class="appointment-card">
            <div class="appointment-header">
                <i class="fas fa-calendar-check"></i>
                <h3>Available Appointments</h3>
            </div>
            
            <div class="appointment-types">
                <h4>Choose Appointment Type:</h4>
                ${appointmentTypesHTML}
            </div>
            
            <div class="time-slots">
                <h4>Available Times:</h4>
                <div class="time-slots-grid">
                    ${timeSlotsHTML}
                </div>
            </div>
            
            <div class="appointment-form" id="appointment-form" style="display: none;">
                <h4>Schedule Your Appointment</h4>
                <form onsubmit="scheduleAppointment(event)">
                    <input type="hidden" id="selected-appointment-type" />
                    <input type="hidden" id="selected-time-slot" />
                    
                    <div class="form-group">
                        <label>Name:</label>
                        <input type="text" id="appointment-name" required />
                    </div>
                    
                    <div class="form-group">
                        <label>Phone:</label>
                        <input type="tel" id="appointment-phone" required />
                    </div>
                    
                    <div class="form-group">
                        <label>Notes (Optional):</label>
                        <textarea id="appointment-notes"></textarea>
                    </div>
                    
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-check"></i> Schedule Appointment
                        </button>
                        <button type="button" class="btn btn-secondary" onclick="cancelAppointment()">
                            <i class="fas fa-times"></i> Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    container.appendChild(optionsCard);
    container.scrollTop = container.scrollHeight;
}

function showAppointmentConfirmation(appointmentData) {
    console.log('Showing appointment confirmation:', appointmentData);
    
    const container = document.getElementById('chat-messages');
    if (!container) return;
    
    const confirmationCard = document.createElement('div');
    confirmationCard.className = 'appointment-confirmation';
    confirmationCard.innerHTML = `
        <div class="appointment-card success">
            <div class="appointment-header">
                <i class="fas fa-check-circle"></i>
                <h3>Appointment Confirmed!</h3>
            </div>
            <div class="confirmation-details">
                <p><strong>Appointment ID:</strong> ${appointmentData.appointment_id}</p>
                <p><strong>Customer:</strong> ${appointmentData.appointment.customer_name}</p>
                <p><strong>Phone:</strong> ${appointmentData.appointment.customer_phone}</p>
                <p><strong>Type:</strong> ${appointmentData.appointment.appointment_type}</p>
                ${appointmentData.appointment.preferred_date ? `<p><strong>Preferred Date:</strong> ${appointmentData.appointment.preferred_date}</p>` : ''}
                ${appointmentData.appointment.preferred_time ? `<p><strong>Preferred Time:</strong> ${appointmentData.appointment.preferred_time}</p>` : ''}
            </div>
            <div class="next-steps">
                <h4>Next Steps:</h4>
                <ul>
                    <li>Our team will contact you within 24 hours</li>
                    <li>You'll receive a calendar invite</li>
                    <li>Please bring photos and measurements</li>
                </ul>
            </div>
        </div>
    `;
    
    container.appendChild(confirmationCard);
    container.scrollTop = container.scrollHeight;
}

function requestAppointmentOptions() {
    const message = "I'd like to see available appointment times";
    document.getElementById('chat-input').value = message;
    sendMessage();
}

function selectAppointmentType(type) {
    document.getElementById('selected-appointment-type').value = type;
    
    // Highlight selected type
    document.querySelectorAll('.appointment-type').forEach(el => el.classList.remove('selected'));
    event.target.closest('.appointment-type').classList.add('selected');
    
    // Show form if both type and time are selected
    checkAppointmentFormReady();
}

function selectTimeSlot(slot) {
    document.getElementById('selected-time-slot').value = slot;
    
    // Highlight selected time
    document.querySelectorAll('.time-slot').forEach(el => el.classList.remove('selected'));
    event.target.classList.add('selected');
    
    // Show form if both type and time are selected
    checkAppointmentFormReady();
}

function checkAppointmentFormReady() {
    const type = document.getElementById('selected-appointment-type').value;
    const time = document.getElementById('selected-time-slot').value;
    
    if (type && time) {
        document.getElementById('appointment-form').style.display = 'block';
        document.getElementById('appointment-form').scrollIntoView({ behavior: 'smooth' });
    }
}

function scheduleAppointment(event) {
    event.preventDefault();
    
    const type = document.getElementById('selected-appointment-type').value;
    const time = document.getElementById('selected-time-slot').value;
    const name = document.getElementById('appointment-name').value;
    const phone = document.getElementById('appointment-phone').value;
    const notes = document.getElementById('appointment-notes').value;
    
    const message = `Please schedule a ${type} appointment for ${name} at ${time}. Phone: ${phone}. Notes: ${notes}`;
    
    document.getElementById('chat-input').value = message;
    sendMessage();
}

function cancelAppointment() {
    document.querySelector('.appointment-options').remove();
}

function dismissAppointmentSuggestion(button) {
    button.closest('.appointment-suggestion').remove();
}

console.log('✅ External JavaScript file loaded completely');