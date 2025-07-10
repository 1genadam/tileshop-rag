// Fixed Chat functionality - working version
console.log('External JavaScript loaded (fixed version)');

// Global variables
let messageCount = 0;

// Send message function with AOS integration
async function sendMessage() {
    console.log('Send function called (AOS enhanced)');
    const input = document.getElementById('chat-input');
    const phoneInput = document.getElementById('customer-phone');
    const nameInput = document.getElementById('customer-name');
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
        
        const response = await fetch('/api/chat/simple', {
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
            
            // Show tool usage information (optional debug info)
            if (data.tool_calls && data.tool_calls.length > 0) {
                console.log('Tools used:', data.tool_calls.map(tc => tc.tool));
                
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
    if (testContainer) {
        console.log('Container element:', testContainer);
    }
    
    console.log('✅ External JavaScript initialization complete!');
});

console.log('✅ External JavaScript file loaded completely');