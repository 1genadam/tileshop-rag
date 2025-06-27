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

// Sync function
async function syncData() {
    console.log('Sync function called (external)');
    const btn = document.getElementById('sync-data-button');
    if (!btn) return;
    
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="material-icons mr-2">sync</span> Syncing...';
    btn.disabled = true;
    
    try {
        const response = await fetch('/api/rag/sync', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            btn.innerHTML = '<span class="material-icons mr-2">check_circle</span> Synced!';
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }, 2000);
        } else {
            btn.innerHTML = '<span class="material-icons mr-2">error</span> Failed';
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }, 2000);
        }
    } catch (error) {
        console.error('Sync error:', error);
        btn.innerHTML = '<span class="material-icons mr-2">error</span> Failed';
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }, 2000);
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
                <p>${text}</p>
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