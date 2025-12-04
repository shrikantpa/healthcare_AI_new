/**
 * Chat Interface JavaScript Module
 * Handles role-based guidance chat interface
 */

// Global state
let currentUser = null;
let currentLocation = { district: null, state: null };
let conversations = [];
let currentConversationId = null;

/**
 * Initialize chat page
 */
function initializeChat() {
    console.log('🚀 Initializing chat interface...');
    
    // Get user data from localStorage
    const userStr = localStorage.getItem('user');
    if (!userStr) {
        console.warn('❌ No user data found, redirecting to login');
        window.location.href = 'index.html';
        return;
    }
    
    try {
        currentUser = JSON.parse(userStr);
        console.log('✓ User loaded:', currentUser);
        
        // Get location from user profile (set during login)
        if (currentUser.district && currentUser.state) {
            currentLocation = {
                district: currentUser.district,
                state: currentUser.state
            };
            console.log('✓ Location loaded from user profile:', currentLocation);
        } else {
            console.warn('⚠️ No location in user profile');
            currentLocation = { district: null, state: null };
        }
        
        // Update user info in sidebar
        updateUserInfo();
        
        // Auto-load initial guidance if location is available
        if (currentLocation.district && currentLocation.state) {
            setTimeout(() => {
                loadInitialGuidance();
            }, 500);
        } else {
            // Show message if no location
            const chatContent = document.getElementById('chatContent');
            chatContent.innerHTML = '';
            addSystemMessage('Welcome! However, we need your location to generate guidance. Please update your profile.');
        }
        
    } catch (error) {
        console.error('❌ Error parsing user data:', error);
        window.location.href = 'index.html';
    }
}

/**
 * Update user information in sidebar
 */
function updateUserInfo() {
    const username = currentUser.username || 'User';
    const role = currentUser.role || 'Unknown';
    const initial = username.charAt(0).toUpperCase();
    
    // Get location from currentUser object (set during login)
    if (currentUser.district && currentUser.state) {
        currentLocation = {
            district: currentUser.district,
            state: currentUser.state
        };
    }
    
    // Update DOM
    document.getElementById('userInitial').textContent = initial;
    document.getElementById('sidebarUsername').textContent = username;
    document.getElementById('sidebarRole').textContent = role;
    
    const locationDisplay = currentLocation.district ? 
        `📍 ${currentLocation.district}, ${currentLocation.state}` : 
        '📍 No location available';
    document.getElementById('sidebarLocation').innerHTML = locationDisplay;
    
    console.log('✓ User info updated');
}

/**
 * Load initial guidance on page load
 */
async function loadInitialGuidance() {
    console.log('📍 Loading initial guidance...');
    
    const chatContent = document.getElementById('chatContent');
    chatContent.innerHTML = '';
    
    if (!currentLocation.district || !currentLocation.state) {
        addSystemMessage('Welcome! However, we need your location to generate guidance. Please update your profile.');
        return;
    }
    
    // Show loading and fetch guidance
    addSystemMessage('Fetching role-specific guidance for ' + currentLocation.district + ', ' + currentLocation.state + '...');
    await fetchRoleBasedGuidance();
}

/**
 * Fetch role-based guidance from backend
 */
async function fetchRoleBasedGuidance() {
    if (!currentUser || !currentLocation.district || !currentLocation.state) {
        addErrorMessage('Missing required information');
        return;
    }
    
    try {
        showLoadingIndicator();
        
        const requestData = {
            username: currentUser.username,
            password: localStorage.getItem('userPassword') || '',
            district: currentLocation.district,
            state: currentLocation.state
        };
        
        console.log('📤 Requesting guidance:', requestData);
        
        const response = await fetch(`${API_BASE_URL}/guidance`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        console.log('📥 Guidance received:', data);
        
        hideLoadingIndicator();
        
        if (response.ok && data.status === 'success') {
            displayGuidance(data);
            
            // Save this guidance to conversations
            addConversation(data);
        } else if (data.status === 'no_data') {
            addErrorMessage('No outbreak data available for ' + currentLocation.district);
        } else {
            addErrorMessage(data.message || 'Error loading guidance');
        }
    } catch (error) {
        console.error('❌ Error fetching guidance:', error);
        hideLoadingIndicator();
        addErrorMessage('Error: ' + error.message);
    }
}

/**
 * Display guidance in chat
 */
function displayGuidance(guidanceData) {
    const { role, district, state, forecast, guidance, message } = guidanceData;
    
    // Add header message
    addAssistantMessage(`
        <strong>📊 ${message}</strong>
        <div style="margin-top: 10px; padding: 10px; background: #f0f0f0; border-radius: 6px;">
            <strong>Role:</strong> <span class="role-badge">${role}</span>
            <strong style="display: block; margin-top: 8px;">Location:</strong> ${district}, ${state}
        </div>
    `);
    
    // Display forecast data if available
    if (forecast) {
        displayForecastData(forecast, role);
    }
    
    // Display role-specific guidance
    if (guidance) {
        displayRoleSpecificGuidance(role, guidance);
    }
}

/**
 * Display forecast data
 */
function displayForecastData(forecast, role) {
    let forecastHtml = '<div class="guidance-card"><h3>📈 Outbreak Forecast Data</h3>';
    
    if (role === 'SCMO' && forecast.districts) {
        // State-level display
        forecastHtml += '<p><strong>District-wise Analysis:</strong></p>';
        forecastHtml += '<div style="margin-top: 10px;">';
        
        forecast.districts.forEach(dist => {
            const f = dist.forecast;
            if (f) {
                const statusClass = `status-${f.outbreak_status?.replace(/_/g, '-') || 'low-risk'}`;
                forecastHtml += `
                    <div style="padding: 10px; margin: 8px 0; background: #f9f9f9; border-radius: 6px;">
                        <strong>${dist.district}</strong>
                        <span class="status-badge ${statusClass}">${f.outbreak_status || 'Low Risk'}</span>
                        <div style="font-size: 12px; margin-top: 5px; color: #666;">
                            Expected Cases: <strong>${f.total_expected_cases || 0}</strong>
                        </div>
                    </div>
                `;
            }
        });
        
        forecastHtml += '</div>';
    } else if (forecast.outbreak_status) {
        // District-level display
        const statusClass = `status-${forecast.outbreak_status?.replace(/_/g, '-') || 'low-risk'}`;
        forecastHtml += `
            <div class="forecast-data">
                <span class="status-badge ${statusClass}">${forecast.outbreak_status || 'Low Risk'}</span>
                <div style="margin-top: 10px;">
                    <strong>💉 Disease:</strong> ${forecast.disease_name || 'Unknown'}<br>
                    <strong>👥 Expected Cases:</strong> ${forecast.total_expected_cases || 0}<br>
                    <strong>🧑 Male Cases:</strong> ${forecast.forecast_by_gender?.male || 0}<br>
                    <strong>👩 Female Cases:</strong> ${forecast.forecast_by_gender?.female || 0}
                </div>
            </div>
        `;
    }
    
    forecastHtml += '</div>';
    addAssistantMessage(forecastHtml);
}

/**
 * Display role-specific guidance
 */
function displayRoleSpecificGuidance(role, guidance) {
    let guidanceHtml = '<div class="guidance-card"><h3>✅ Role-Specific Guidance</h3>';
    
    if (role === 'ASHA') {
        guidanceHtml += displayASHAGuidance(guidance);
    } else if (role === 'DCMO') {
        guidanceHtml += displayDCMOGuidance(guidance);
    } else if (role === 'SCMO') {
        guidanceHtml += displaySCMOGuidance(guidance);
    }
    
    guidanceHtml += '</div>';
    addAssistantMessage(guidanceHtml);
}

/**
 * Display ASHA-specific guidance
 */
function displayASHAGuidance(guidance) {
    return `
        <div class="guidance-section">
            <strong>🏥 General Remedies</strong>
            <p>${guidance.general_remedies || 'No data available'}</p>
        </div>
        <div class="guidance-section">
            <strong>👥 Social Remedies</strong>
            <p>${guidance.social_remedies || 'No data available'}</p>
        </div>
        <div class="guidance-section">
            <strong>🏛️ Government Regulatory Actions</strong>
            <p>${guidance.govt_regulatory_actions || 'No data available'}</p>
        </div>
        <div class="guidance-section">
            <strong>🩺 Healthcare Body Actions</strong>
            <p>${guidance.healthcare_body_actions || 'No data available'}</p>
        </div>
    `;
}

/**
 * Display DCMO-specific guidance
 */
function displayDCMOGuidance(guidance) {
    return `
        <div class="guidance-section">
            <strong>📊 Cases Identified</strong>
            <p>${guidance.cases_identified || 0} cases identified in district</p>
        </div>
        <div class="guidance-section">
            <strong>🏥 Department Actions</strong>
            <p>${guidance.department_actions || 'No data available'}</p>
        </div>
        <div class="guidance-section">
            <strong>📦 Inventory Arrangements</strong>
            <p>${guidance.inventory_arrangements || 'No data available'}</p>
        </div>
        <div class="guidance-section">
            <strong>👨‍⚕️ Resource Deployment</strong>
            <p>${guidance.resource_deployment || 'No data available'}</p>
        </div>
        <div class="guidance-section">
            <strong>🤝 Coordination Plan</strong>
            <p>${guidance.coordination_plan || 'No data available'}</p>
        </div>
        <div class="guidance-section">
            <strong>💰 Budget Allocation</strong>
            <p>${guidance.budget_allocation || 'No data available'}</p>
        </div>
    `;
}

/**
 * Display SCMO-specific guidance
 */
function displaySCMOGuidance(guidance) {
    return `
        <div class="guidance-section">
            <strong>🌍 State Overview</strong>
            <p>${guidance.state_overview || 'No data available'}</p>
        </div>
        <div class="guidance-section">
            <strong>🔴 Highly Affected Districts</strong>
            <p>${guidance.highly_affected_districts || 'No data available'}</p>
        </div>
        <div class="guidance-section">
            <strong>📈 Comparative Analysis</strong>
            <p>${guidance.comparative_analysis || 'No data available'}</p>
        </div>
        <div class="guidance-section">
            <strong>💊 State-level Remedies</strong>
            <p>${guidance.state_level_remedies || 'No data available'}</p>
        </div>
        <div class="guidance-section">
            <strong>👨‍⚕️ Medical Professional Deployment</strong>
            <p>${guidance.medical_professional_deployment || 'No data available'}</p>
        </div>
        <div class="guidance-section">
            <strong>⚠️ Emergency Measures</strong>
            <p>${guidance.emergency_measures || 'No data available'}</p>
        </div>
        <div class="guidance-section">
            <strong>🔗 Inter-District Coordination</strong>
            <p>${guidance.inter_district_coordination || 'No data available'}</p>
        </div>
        <div class="guidance-section">
            <strong>💰 Emergency Funding</strong>
            <p>${guidance.emergency_funding || 'No data available'}</p>
        </div>
        <div class="guidance-section">
            <strong>📅 Timeline & Milestones</strong>
            <p>${guidance.timeline_and_milestones || 'No data available'}</p>
        </div>
    `;
}

/**
 * Add system message to chat
 */
function addSystemMessage(text) {
    const chatContent = document.getElementById('chatContent');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system';
    messageDiv.innerHTML = `<div class="message-content">${text}</div>`;
    
    chatContent.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Add assistant message to chat
 */
function addAssistantMessage(html) {
    const chatContent = document.getElementById('chatContent');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">${html}</div>
    `;
    
    chatContent.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Add error message to chat
 */
function addErrorMessage(text) {
    const chatContent = document.getElementById('chatContent');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system';
    messageDiv.innerHTML = `<div class="message-content" style="background: #ffe0e0; color: #d32f2f;">❌ ${text}</div>`;
    
    chatContent.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Send message (for future chat interactions)
 */
async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    const chatContent = document.getElementById('chatContent');
    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'message user';
    userMessageDiv.innerHTML = `
        <div class="message-content">${escapeHtml(message)}</div>
        <div class="message-avatar">${currentUser.username.charAt(0).toUpperCase()}</div>
    `;
    chatContent.appendChild(userMessageDiv);
    
    input.value = '';
    input.style.height = 'auto';
    scrollToBottom();
    
    // Handle specific commands
    if (message.toLowerCase().includes('guidance') || message.toLowerCase().includes('reload') || 
        message.toLowerCase().includes('remedy') || message.toLowerCase().includes('remedies') ||
        message.toLowerCase().includes('action') || message.toLowerCase().includes('what') ||
        message.toLowerCase().includes('suggest') || message.toLowerCase().includes('implement')) {
        addSystemMessage('Fetching role-specific guidance and remedies...');
        await fetchRoleBasedGuidance();
    } else if (message.toLowerCase().includes('location') || message.toLowerCase().includes('change')) {
        showLocationPrompt();
    } else {
        addAssistantMessage('I\'m here to help with outbreak guidance based on your role. Try asking for "guidance", "remedies", "what actions", or ask me to "reload" for the latest information. You can also "change location" if needed.');
    }
}

/**
 * Handle input keydown for auto-resize
 */
function handleInputKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    } else {
        // Auto-resize textarea
        const textarea = event.target;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px';
    }
}

/**
 * Start new chat
 */
function startNewChat() {
    document.getElementById('chatContent').innerHTML = '';
    addSystemMessage('Starting new guidance request...');
    loadInitialGuidance();
}

/**
 * Add conversation to history
 */
function addConversation(data) {
    const id = Date.now();
    const conv = {
        id,
        title: `${data.role} - ${data.district}`,
        timestamp: new Date().toLocaleString(),
        data
    };
    
    conversations.unshift(conv);
    currentConversationId = id;
    
    updateConversationList();
}

/**
 * Update conversation list in sidebar
 */
function updateConversationList() {
    const list = document.getElementById('conversationList');
    
    if (conversations.length === 0) {
        list.innerHTML = '<p style="text-align: center; color: #aaa; font-size: 13px; padding: 20px 0;">No conversations yet</p>';
        return;
    }
    
    list.innerHTML = '';
    
    conversations.forEach(conv => {
        const item = document.createElement('div');
        item.className = `conversation-item ${conv.id === currentConversationId ? 'active' : ''}`;
        item.textContent = conv.title;
        item.onclick = () => selectConversation(conv.id);
        list.appendChild(item);
    });
}

/**
 * Select conversation
 */
function selectConversation(id) {
    const conv = conversations.find(c => c.id === id);
    if (conv) {
        currentConversationId = id;
        document.getElementById('chatContent').innerHTML = '';
        displayGuidance(conv.data);
        updateConversationList();
    }
}

/**
 * Show loading indicator
 */
function showLoadingIndicator() {
    const chatContent = document.getElementById('chatContent');
    const loader = document.createElement('div');
    loader.className = 'loading-indicator';
    loader.id = 'loadingIndicator';
    loader.innerHTML = '<span>Loading guidance</span><div class="dot"></div><div class="dot"></div><div class="dot"></div>';
    chatContent.appendChild(loader);
    scrollToBottom();
}

/**
 * Hide loading indicator
 */
function hideLoadingIndicator() {
    const loader = document.getElementById('loadingIndicator');
    if (loader) loader.remove();
}

/**
 * Scroll to bottom of chat
 */
function scrollToBottom() {
    const chatContent = document.getElementById('chatContent');
    setTimeout(() => {
        chatContent.scrollTop = chatContent.scrollHeight;
    }, 100);
}

/**
 * Escape HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Handle logout
 */
function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('user');
        localStorage.removeItem('userPassword');
        localStorage.removeItem('userLocation');
        window.location.href = 'index.html';
    }
}

/**
 * Initialize on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 Chat page loaded');
    initializeChat();
});

console.log('✓ Chat module loaded successfully');
