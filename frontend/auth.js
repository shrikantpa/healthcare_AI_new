/**
 * Authentication JavaScript Module
 * Handles login, signup, and API interactions with enhanced UX
 */

// ==================== API URL CONFIGURATION ====================

// API Base URL points to backend on localhost:8000
const API_BASE_URL = 'http://localhost:8000';

// Log API configuration for debugging
console.log('🔌 Frontend Host:', window.location.hostname);
console.log('🔌 API Base URL:', API_BASE_URL);
console.log('🔌 Protocol:', window.location.protocol);

// ==================== UTILITY FUNCTIONS ====================

/**
 * Show loading spinner with animation
 */
function showSpinner() {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.style.display = 'flex';
        spinner.classList.add('active');
    }
}

/**
 * Hide loading spinner
 */
function hideSpinner() {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.classList.remove('active');
        setTimeout(() => {
            spinner.style.display = 'none';
        }, 300);
    }
}

/**
 * Show error message with animation
 */
function showError(message, duration = 5000) {
    const errorDiv = document.getElementById('errorMessage');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        errorDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        console.log('❌ Error shown:', message);
        
        // Auto-hide after duration
        setTimeout(() => {
            hideError();
        }, duration);
    } else {
        console.error('❌ Error message div not found. Message was:', message);
        alert(message);
    }
}

/**
 * Hide error message with animation
 */
function hideError() {
    const errorDiv = document.getElementById('errorMessage');
    if (errorDiv) {
        errorDiv.style.opacity = '0';
        setTimeout(() => {
            errorDiv.style.display = 'none';
            errorDiv.style.opacity = '1';
        }, 300);
    }
}

/**
 * Show success message
 */
function showSuccess(message, duration = 3000) {
    const successDiv = document.getElementById('successMessage');
    if (successDiv) {
        successDiv.textContent = message;
        successDiv.style.display = 'block';
        successDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        setTimeout(() => {
            hideSuccess();
        }, duration);
    }
}

/**
 * Hide success message
 */
function hideSuccess() {
    const successDiv = document.getElementById('successMessage');
    if (successDiv) {
        successDiv.style.opacity = '0';
        setTimeout(() => {
            successDiv.style.display = 'none';
            successDiv.style.opacity = '1';
        }, 300);
    }
}

/**
 * Make API call with error handling and retry logic
 */
async function makeApiCall(endpoint, method = 'GET', data = null, retries = 3) {
    let lastError = null;
    
    for (let attempt = 1; attempt <= retries; attempt++) {
        try {
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                mode: 'cors',
                cache: 'no-cache',
                credentials: 'omit',
            };

            if (data) {
                options.body = JSON.stringify(data);
            }

            console.log(`🔄 API Call (Attempt ${attempt}/${retries}): ${method} ${API_BASE_URL}${endpoint}`);
            console.log('📨 Request Headers:', options.headers);
            console.log('📦 Request Data:', data);
            
            const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
            const result = await response.json();

            console.log(`✓ API Response Status: ${response.status}`);
            console.log('📥 Response Headers:', {
                'Content-Type': response.headers.get('content-type'),
                'Content-Length': response.headers.get('content-length'),
            });
            console.log('📄 Response Data:', result);
            
            return {
                success: response.ok,
                status: response.status,
                data: result,
            };
        } catch (error) {
            lastError = error;
            console.error(`🔴 API Error (Attempt ${attempt}/${retries}):`, error);
            console.error('Error Details:', {
                message: error.message,
                stack: error.stack,
                name: error.name,
            });
            
            // Wait before retrying (except on last attempt)
            if (attempt < retries) {
                await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
            }
        }
    }
    
    console.error('🔴 API Failed after all retries:', lastError);
    return {
        success: false,
        status: 0,
        data: { detail: 'Network error. Please ensure backend is running on:', API_BASE_URL},
    };
}

/**
 * Debounce function for input validation
 */
function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

// ==================== LOGIN FUNCTIONALITY ====================

/**
 * Initialize login form with event handlers
 */
function initializeLoginForm() {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;

    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');

    // Add focus animations
    if (usernameInput) {
        usernameInput.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.02)';
        });
        usernameInput.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    }

    if (passwordInput) {
        passwordInput.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.02)';
        });
        passwordInput.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    }

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleLogin();
    });

    console.log('✓ Login form initialized');
}

/**
 * Handle login submission
 */
async function handleLogin() {
    hideError();
    hideSuccess();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    console.log('🔐 Login Attempt:', { username, passwordLength: password.length });

    // Validation
    if (!username || !password) {
        showError('Please enter both username and password');
        return;
    }

    if (username.length < 3) {
        showError('Username must be at least 3 characters');
        return;
    }

    showSpinner();

    try {
        const loginData = { username, password };
        console.log('📤 Sending login request:', loginData);
        
        const result = await makeApiCall('/login', 'POST', loginData);

        console.log('✓ Login response received:', result);

        if (result.success) {
            console.log('✓ Login successful');
            console.log('👤 User data:', result.data);
            
            // Store complete user data in localStorage
            localStorage.setItem('user', JSON.stringify({
                user_id: result.data.user_id,
                username: result.data.username,
                role: result.data.role,
                first_name: result.data.first_name,
                last_name: result.data.last_name,
                district: result.data.district,
                state: result.data.state,
                created_at: result.data.created_at
            }));
            localStorage.setItem('userPassword', password);
            
            // Store location data if available
            if (result.data.district && result.data.state) {
                localStorage.setItem('userLocation', JSON.stringify({
                    district: result.data.district,
                    state: result.data.state
                }));
                console.log('✓ Location data stored:', result.data.district, result.data.state);
            }
            
            localStorage.setItem('token', result.data.username);

            showSuccess('✓ Login successful! Redirecting...');
            setTimeout(() => {
                window.location.href = 'chat.html';
            }, 1200);
        } else {
            const errorMsg = result.data.detail || 'Invalid username or password';
            console.error('❌ Login failed:', errorMsg);
            showError('❌ ' + errorMsg);
        }
    } catch (error) {
        console.error('🔴 Login error:', error);
        showError('An error occurred during login. Please try again.');
    } finally {
        hideSpinner();
    }
}

// ==================== SIGNUP FUNCTIONALITY ====================

/**
 * Initialize signup form with validation
 */
function initializeSignupForm() {
    const signupForm = document.getElementById('signupForm');
    if (!signupForm) return;

    const passwordInput = document.getElementById('signupPassword');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const stateSelect = document.getElementById('state');

    // Password matching validation with real-time feedback
    if (passwordInput && confirmPasswordInput) {
        const passwordMatchDiv = document.getElementById('passwordMatch');

        confirmPasswordInput.addEventListener('input', debounce(() => {
            if (passwordInput.value && confirmPasswordInput.value) {
                if (passwordInput.value === confirmPasswordInput.value) {
                    passwordMatchDiv.textContent = '✓ Passwords match';
                    passwordMatchDiv.classList.remove('error');
                    passwordMatchDiv.classList.add('success');
                    confirmPasswordInput.style.borderColor = 'var(--success-color)';
                } else {
                    passwordMatchDiv.textContent = '✗ Passwords do not match';
                    passwordMatchDiv.classList.add('error');
                    passwordMatchDiv.classList.remove('success');
                    confirmPasswordInput.style.borderColor = 'var(--error-color)';
                }
            } else {
                passwordMatchDiv.textContent = '';
                confirmPasswordInput.style.borderColor = '';
            }
        }, 300));
    }

    // State change event for cascading dropdown
    if (stateSelect) {
        stateSelect.addEventListener('change', () => {
            updateDistrictDropdown();
        });
    }

    // Form submission
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleSignup();
    });

    // Add form group animations
    const formGroups = signupForm.querySelectorAll('.form-group');
    formGroups.forEach((group, index) => {
        group.style.animationDelay = `${index * 50}ms`;
    });

    console.log('✓ Signup form initialized');
}

/**
 * Load location data from backend API with better error handling
 */
async function loadLocationData() {
    try {
        console.log('📍 Loading location data from:', API_BASE_URL + '/locations');
        const result = await makeApiCall('/locations', 'GET');

        console.log('📍 API Result:', result);

        if (result.success && result.data && result.data.length > 0) {
            console.log('✓ Locations loaded:', result.data.length, 'locations');
            populateStateDropdown(result.data);
        } else if (result.success && Array.isArray(result.data)) {
            console.log('✓ Locations loaded:', result.data.length, 'locations');
            populateStateDropdown(result.data);
        } else {
            console.error('❌ Failed to load locations. Response:', result);
            showError('⚠️ Could not load location data. Please check if backend is running on http://localhost:8000 and try refreshing.');
        }
    } catch (error) {
        console.error('🔴 Error loading locations:', error);
        showError('❌ Error loading location data: ' + error.message);
    }
}

/**
 * Populate state dropdown from locations data
 */
function populateStateDropdown(locations) {
    const stateSelect = document.getElementById('state');
    if (!stateSelect) {
        console.error('❌ State select element not found');
        return;
    }

    if (!locations || locations.length === 0) {
        console.error('❌ No locations provided');
        showError('❌ No location data available');
        return;
    }

    // Get unique states and sort
    const states = [...new Set(locations.map((loc) => loc.state))].sort();
    
    console.log('📍 Processing', states.length, 'unique states:', states);

    // Clear existing options (keep placeholder)
    stateSelect.innerHTML = '<option value="">-- Select State --</option>';

    // Add states to dropdown
    states.forEach((state) => {
        const option = document.createElement('option');
        option.value = state;
        option.textContent = state;
        option.classList.add('state-option');
        stateSelect.appendChild(option);
    });

    // Store all locations data for filtering
    window.allLocations = locations;
    console.log('✓ State dropdown populated with', states.length, 'states. Stored', locations.length, 'location records.');
}

/**
 * Update district dropdown based on selected state
 */
function updateDistrictDropdown() {
    const stateSelect = document.getElementById('state');
    const districtSelect = document.getElementById('district');

    if (!stateSelect || !districtSelect) return;

    const selectedState = stateSelect.value;
    districtSelect.innerHTML = '<option value="">-- Select District --</option>';

    if (!selectedState || !window.allLocations) return;

    // Filter districts by selected state
    const districts = window.allLocations
        .filter((loc) => loc.state === selectedState)
        .map((loc) => loc.district)
        .sort();

    // Add districts to dropdown
    districts.forEach((district) => {
        const option = document.createElement('option');
        option.value = district;
        option.textContent = district;
        option.classList.add('district-option');
        districtSelect.appendChild(option);
    });

    console.log('✓ District dropdown updated with', districts.length, 'districts');
}

/**
 * Handle signup form submission
 */
async function handleSignup() {
    hideError();
    hideSuccess();

    // Get form values
    const firstName = document.getElementById('firstName').value.trim();
    const lastName = document.getElementById('lastName').value.trim();
    const state = document.getElementById('state').value;
    const district = document.getElementById('district').value;
    const role = document.getElementById('role').value;
    const username = document.getElementById('signupUsername').value.trim();
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    // Comprehensive validation
    if (!firstName) {
        showError('Please enter your first name');
        return;
    }

    if (firstName.length < 2) {
        showError('First name must be at least 2 characters');
        return;
    }

    if (!lastName) {
        showError('Please enter your last name');
        return;
    }

    if (lastName.length < 2) {
        showError('Last name must be at least 2 characters');
        return;
    }

    if (!state) {
        showError('Please select a state');
        return;
    }

    if (!district) {
        showError('Please select a district');
        return;
    }

    if (!role) {
        showError('Please select a role');
        return;
    }

    if (!username) {
        showError('Please enter a username');
        return;
    }

    if (username.length < 3) {
        showError('Username must be at least 3 characters');
        return;
    }

    if (!password || password.length < 6) {
        showError('Password must be at least 6 characters');
        return;
    }

    if (password !== confirmPassword) {
        showError('Passwords do not match');
        return;
    }

    console.log('📝 Submitting signup form...');
    showSpinner();

    try {
        const result = await makeApiCall('/signup', 'POST', {
            first_name: firstName,
            last_name: lastName,
            username,
            password,
            district,
            state,
            role,
        });

        if (result.success) {
            console.log('✓ Signup successful');
            
            // Store user data for auto-login
            const userData = result.data;
            localStorage.setItem('user', JSON.stringify({
                user_id: userData.user_id,
                username: userData.username,
                role: userData.role
            }));
            localStorage.setItem('userPassword', password);
            localStorage.setItem('userLocation', JSON.stringify({
                district: userData.district,
                state: userData.state
            }));
            
            // Show success modal
            showSuccessModal();
            // Reset form
            document.getElementById('signupForm').reset();
            
            // Redirect to chat after 2 seconds
            setTimeout(() => {
                window.location.href = 'chat.html';
            }, 2000);
        } else {
            const errorMsg = result.data.detail || 'Signup failed';
            if (errorMsg.includes('already exists') || errorMsg.includes('duplicate')) {
                showError('❌ Username already exists. Please try a different username.');
            } else if (errorMsg.includes('does not exist') || errorMsg.includes('not found')) {
                showError('❌ Invalid location selected. Please select a valid district and state.');
            } else if (errorMsg.includes('Invalid role')) {
                showError('❌ Invalid role selected. Please select a valid role.');
            } else {
                showError('❌ ' + errorMsg);
            }
        }
    } catch (error) {
        console.error('🔴 Signup error:', error);
        showError('An error occurred during signup. Please try again.');
    } finally {
        hideSpinner();
    }
}

/**
 * Show success modal with animation
 */
function showSuccessModal() {
    const modal = document.getElementById('successModal');
    if (modal) {
        modal.style.display = 'flex';
        modal.classList.add('active');
        console.log('✓ Success modal displayed');
    }
}

/**
 * Close success modal
 */
function closeSuccessModal() {
    const modal = document.getElementById('successModal');
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }
}

// ==================== PAGE INITIALIZATION ====================

/**
 * Handle page visibility for cleanup
 */
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        console.log('📱 Page is visible');
        hideSpinner();
    }
});

/**
 * Keyboard shortcuts
 */
document.addEventListener('keydown', (e) => {
    // Enter to submit form
    if (e.key === 'Enter') {
        const activeForm = document.activeElement.closest('form');
        if (activeForm) {
            const submitBtn = activeForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.click();
            }
        }
    }
    
    // Escape to close modal
    if (e.key === 'Escape') {
        const modal = document.getElementById('successModal');
        if (modal && modal.style.display !== 'none') {
            closeSuccessModal();
        }
    }
});

/**
 * Initialize on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    const currentPage = window.location.pathname;
    const currentFile = window.location.pathname.split('/').pop() || 'index.html';
    
    console.log('🚀 Page loaded:', currentPage);
    console.log('📄 Current file:', currentFile);
    console.log('🔌 API Base URL:', API_BASE_URL);

    if (currentPage.includes('signup') || currentFile === 'signup.html' || currentFile.includes('signup')) {
        console.log('📝 Initializing signup page...');
        initializeSignupForm();
        
        // Load locations with small delay to ensure DOM is ready
        setTimeout(() => {
            console.log('📍 Loading locations...');
            loadLocationData();
        }, 100);
    } else if (currentPage.includes('index') || currentPage.includes('login') || currentPage === '/' || currentFile === 'index.html') {
        console.log('🔐 Initializing login page...');
        initializeLoginForm();
    }
});

console.log('✓ Auth module loaded successfully');
