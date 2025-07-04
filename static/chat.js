// Fixed Chat functionality - working version
console.log('External JavaScript loaded (fixed version)');

// Global variables
let messageCount = 0;

// Send message function
async function sendMessage() {
    console.log('Send function called (external)');
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) {
        alert('Please enter a message');
        return;
    }
    
    // Add user message
    addMessage(message, 'user');
    input.value = '';
    updateCharCount();
    
    // Send to API
    try {
        const response = await fetch('/api/rag/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: message })
        });
        
        const data = await response.json();
        
        console.log('API Response:', data);
        if (data.success) {
            console.log('Adding assistant message:', data.response);
            addMessage(data.response, 'assistant');
        } else {
            console.log('Adding error message:', data.error);
            addMessage('Error: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Send error:', error);
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
                <p>Hello! How can I help you find the perfect tiles today?</p>
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