// Main application state and logic
const app = {
    // --- State Variables ---
    currentPage: 'login', // 'login', 'register', 'mainApp'
    currentMainPage: 'home', // 'home', 'upload', 'dashboard', 'contact'
    authToken: null,
    username: 'User',
    dashboardData: [],

    // --- DOM Element References ---
    elements: {
        // Auth Pages
        authContainer: document.getElementById('authContainer'),
        loginFormContainer: document.getElementById('loginFormContainer'),
        registerFormContainer: document.getElementById('registerFormContainer'),
        loginForm: document.getElementById('loginForm'),
        registerForm: document.getElementById('registerForm'),
        showRegisterPageLink: document.getElementById('showRegisterPage'),
        showLoginPageLink: document.getElementById('showLoginPage'),

        // Main App Layout
        mainAppLayout: document.getElementById('mainAppLayout'),
        usernameDisplay: document.getElementById('usernameDisplay'),
        logoutButton: document.getElementById('logoutButton'),

        // Navigation Links
        navLinks: document.querySelectorAll('.nav-link'), // All navigation links

        // Content Sections
        homeContent: document.getElementById('homeContent'),
        uploadContent: document.getElementById('uploadContent'),
        dashboardContent: document.getElementById('dashboardContent'),
        contactContent: document.getElementById('contactContent'),

        // Upload Forms
        inventoryUploadForm: document.getElementById('inventoryUploadForm'),
        salesUploadForm: document.getElementById('salesUploadForm'),
        addBatchForm: document.getElementById('addBatchForm'),
        addBulkBatchForm: document.getElementById('addBulkBatchForm'),
        bulkBatchJsonInput: document.getElementById('bulk-batch-json'),

        // Dashboard Elements
        refreshDashboardButton: document.getElementById('refreshDashboardButton'),
        dashboardTableBody: document.getElementById('dashboardTableBody'),

        // Global Overlays
        loadingSpinner: document.getElementById('loadingSpinner'),
        messageModal: document.getElementById('messageModal'),
        modalTitle: document.getElementById('modalTitle'),
        modalMessage: document.getElementById('modalMessage'),
        modalCloseButton: document.getElementById('modalCloseButton'),
    },

    // --- Initialization ---
    init() {
        this.addEventListeners();
        // Check for existing token on load
        const storedToken = localStorage.getItem('authToken');
        if (storedToken) {
            this.authToken = storedToken;
            this.showPage('mainApp'); // Go directly to app if token exists
        } else {
            this.showPage('login'); // Otherwise show login
        }
        // Handle hash changes for navigation (e.g., back/forward buttons)
        window.addEventListener('hashchange', this.handleHashChange.bind(this));
        // Removed initial call to handleHashChange here, let showPage handle it
    },

     // --- Handle URL Hash Changes ---
     handleHashChange() {
        // Only handle hash changes when in the main app
        if (this.currentPage === 'mainApp') {
            const hash = window.location.hash.substring(1); // Get hash without '#'
            const validPages = ['home', 'upload', 'dashboard', 'contact'];
            const targetPage = validPages.includes(hash) ? hash : 'home'; // Default to 'home'
            // Only update if the target page is different from the current one
            if (targetPage !== this.currentMainPage) {
                 this.showMainPage(targetPage);
            }
        }
    },


    // --- Page Management ---
    showPage(pageName) {
        // Only update if the page is actually changing
        if (this.currentPage === pageName && document.body.classList.contains('auth-active') === (pageName !== 'mainApp') ) return;


        this.currentPage = pageName;
        document.body.classList.toggle('auth-active', pageName !== 'mainApp');
        this.elements.authContainer.classList.toggle('hidden', pageName === 'mainApp');
        this.elements.mainAppLayout.classList.toggle('hidden', pageName !== 'mainApp');

        if (pageName === 'mainApp') {
            this.fetchCurrentUser().then(() => { // Ensure user is fetched before determining initial page
                const justRegistered = localStorage.getItem('justRegistered') === 'true';
                localStorage.removeItem('justRegistered'); // Clear the flag immediately

                // Determine initial page based on hash or registration status
                const initialHash = window.location.hash.substring(1);
                const validPages = ['home', 'upload', 'dashboard', 'contact'];
                let initialPage = validPages.includes(initialHash) ? initialHash : 'home';

                if (justRegistered) {
                    initialPage = 'home'; // Start on home after registration
                    this.showMainPage(initialPage); // Show home page first
                     // Then scroll to "How It Works"
                    setTimeout(() => {
                        const howItWorksSection = document.querySelector('#homeContent > div:nth-child(2)');
                        if (howItWorksSection) {
                            howItWorksSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            this.showMessage('Registration successful! Welcome. Learn how VentaRiko works below.', false);
                        } else {
                            this.showMessage('Registration successful! Welcome to VentaRiko.', false);
                        }
                    }, 300);
                } else {
                     // Check hash again in case it changed during async fetchCurrentUser
                     const currentHash = window.location.hash.substring(1);
                     initialPage = validPages.includes(currentHash) ? currentHash : 'home';
                     this.showMainPage(initialPage); // Show page based on hash or default to home
                }
            }).catch(() => {
                 // If fetchCurrentUser failed (logged out), stay on login page
                 this.showPage('login');
            });

        } else {
            // Reset forms if showing auth pages
            this.elements.loginForm.reset();
            this.elements.registerForm.reset();
             window.location.hash = ''; // Clear hash when logging out or going to auth
        }
    },

    showAuthForm(formType) {
        this.elements.loginFormContainer.classList.toggle('hidden', formType !== 'login');
        this.elements.registerFormContainer.classList.toggle('hidden', formType !== 'register');
    },

    showMainPage(pageName) {
        // Prevent unnecessary re-renders ONLY if target page is already visible
        const targetContent = document.getElementById(pageName + 'Content');
        if (this.currentMainPage === pageName && targetContent && !targetContent.classList.contains('hidden')) {
             // If navigating to dashboard, still refresh data
             if(pageName === 'dashboard') this.fetchDashboard();
             return;
        }


        this.currentMainPage = pageName;

        // Hide all content sections immediately
        document.querySelectorAll('.page-content').forEach(section => {
            section.classList.add('hidden');
            section.classList.remove('active', 'fade-in');
        });

        // Deactivate all nav links
        this.elements.navLinks.forEach(link => link.classList.remove('active'));

        // Show the target content section and activate its nav link
        // const targetContent = document.getElementById(pageName + 'Content'); // Already defined above
        const activeNavLink = document.querySelector(`.nav-link[data-target="${pageName}Content"]`);

        if (targetContent) {
             // Use a tiny delay to ensure 'hidden' is processed before adding 'active' for animation
             setTimeout(() => {
                targetContent.classList.remove('hidden');
                targetContent.classList.add('active', 'fade-in'); // Add active and animation class
                window.scrollTo(0, 0); // Scroll to top when changing page
             }, 10); // Small delay like 10ms is often enough

            if (activeNavLink) {
                activeNavLink.classList.add('active');
            }
            // Update URL hash only if it's different
             if (window.location.hash !== `#${pageName}`) {
                window.location.hash = pageName;
             }

            // Fetch dashboard data ONLY when navigating to dashboard
            if (pageName === 'dashboard') {
                this.fetchDashboard();
            }
        } else {
             console.error(`Content section not found for page: ${pageName}`);
             // Fallback to home if target not found
             this.showMainPage('home');
        }
    },


    // --- Event Listeners ---
    addEventListeners() {
        // Auth page navigation
        this.elements.showRegisterPageLink.addEventListener('click', (e) => {
            e.preventDefault();
            this.showAuthForm('register');
        });
        this.elements.showLoginPageLink.addEventListener('click', (e) => {
            e.preventDefault();
            this.showAuthForm('login');
        });

        // Main app navigation - Listen on nav container for delegation
        const navContainer = document.querySelector('nav .hidden.md\\:flex'); // More specific selector
        if(navContainer){
            navContainer.addEventListener('click', (e) => {
                 // Check if the clicked element itself is a nav-link
                 let targetLink = e.target;
                 if (!targetLink.classList.contains('nav-link')) {
                     // If not, check if its parent is a nav-link (e.g., clicking inside the span)
                     targetLink = targetLink.closest('.nav-link');
                 }
                
                if (targetLink && targetLink.classList.contains('nav-link')) {
                    e.preventDefault();
                    const targetId = targetLink.dataset.target;
                    if(targetId){
                        const pageName = targetId.replace('Content', '');
                        this.showMainPage(pageName);
                    }
                }
            });
        }


        // Auth forms
        this.elements.loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        this.elements.registerForm.addEventListener('submit', (e) => this.handleRegister(e));

        // Main app actions
        this.elements.logoutButton.addEventListener('click', () => this.handleLogout());
        this.elements.inventoryUploadForm.addEventListener('submit', (e) => this.handleFileUpload(e, '/setup/upload-inventory/'));
        this.elements.salesUploadForm.addEventListener('submit', (e) => this.handleFileUpload(e, '/sales/upload-daily/'));
        this.elements.addBatchForm.addEventListener('submit', (e) => this.handleAddBatch(e));
        this.elements.addBulkBatchForm.addEventListener('submit', (e) => this.handleBulkAdd(e));
        this.elements.refreshDashboardButton.addEventListener('click', () => this.fetchDashboard());

        // Modal close
        this.elements.modalCloseButton.addEventListener('click', () => this.closeModal());
        this.elements.messageModal.querySelector('.fixed.inset-0').addEventListener('click', () => this.closeModal()); // Background click
    },

    // --- API Handlers ---
     async handleLogin(event) {
        event.preventDefault();
        this.showLoader(true);
        const formData = new FormData(event.target);

        try {
            const response = await fetch('/token', { method: 'POST', body: formData });
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Incorrect username or password');
            }
            const data = await response.json();
            this.authToken = data.access_token;
            localStorage.setItem('authToken', this.authToken); // Store token
            this.showLoader(false);
            this.showPage('mainApp'); // Navigate to main app layout
        } catch (error) {
            this.showLoader(false);
            this.showMessage(`Login Failed: ${error.message}`, true);
        }
    },

    async handleRegister(event) {
        event.preventDefault();
        this.showLoader(true);
        const username = document.getElementById('register-username').value;
        const password = document.getElementById('register-password').value;

        try {
            const response = await fetch('/register/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Registration failed');
            }

            // Attempt auto-login after successful registration
            const loginFormData = new FormData();
            loginFormData.append('username', username);
            loginFormData.append('password', password);

            const loginResponse = await fetch('/token', { method: 'POST', body: loginFormData });
            if (!loginResponse.ok) {
                console.error("Auto-login failed after registration:", await loginResponse.text());
                this.showLoader(false);
                this.showMessage('Registration successful! Please login.', false);
                this.showAuthForm('login'); // Redirect to login form
                this.elements.registerForm.reset();
                return;
            }
            const loginData = await loginResponse.json();
            this.authToken = loginData.access_token;
            localStorage.setItem('authToken', this.authToken);
            localStorage.setItem('justRegistered', 'true'); // Flag for post-login redirection

            this.showLoader(false);
            this.showPage('mainApp'); // Navigate to main app
            this.elements.registerForm.reset();
        } catch (error) {
            this.showLoader(false);
            this.showMessage(`Registration Failed: ${error.message}`, true);
        }
    },

     async fetchCurrentUser() {
        // Use token from localStorage as the primary source
        this.authToken = localStorage.getItem('authToken');
        if (!this.authToken) {
            console.log("No auth token found, cannot fetch current user.");
            // Don't logout here, let showPage handle it if needed
            return Promise.reject("No auth token"); // Reject promise to prevent further actions
        }
        try {
            // Include token in the fetch call
            const response = await this.apiFetch('/users/me/'); // apiFetch handles adding the token
            if (response && response.username) {
                this.username = response.username;
                this.elements.usernameDisplay.textContent = this.username;
                return Promise.resolve(); // Resolve promise on success
            } else {
                 console.error('Invalid response structure from /users/me/');
                 this.handleLogout(); // Logout if user data is invalid
                 return Promise.reject("Invalid user data");
            }
        } catch (error) {
            console.error('Failed to fetch user:', error.message);
            // Error here implies token is bad, logout
            this.handleLogout();
            return Promise.reject(error.message); // Reject promise
        }
    },

    handleLogout() {
        this.authToken = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('justRegistered');
        this.username = 'User';
        this.dashboardData = [];
        if (this.elements.dashboardTableBody) {
             this.elements.dashboardTableBody.innerHTML = '<tr><td colspan="6" class="px-6 py-12 text-center text-gray-500">Click "Refresh Report" to load data.</td></tr>';
        }
        this.showPage('login'); // Redirect to login screen
        window.location.hash = ''; // Clear hash on logout
    },

    async handleFileUpload(event, endpoint) {
        event.preventDefault();
        this.showLoader(true);
        const fileInput = event.target.querySelector('input[type="file"]');
        if (!fileInput || !fileInput.files.length) {
            this.showMessage('Please select a file to upload.', true);
            this.showLoader(false);
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        try {
            const response = await this.apiFetch(endpoint, { method: 'POST', body: formData });

            this.showLoader(false);
            let successMsg = `Success: File "${fileInput.files[0].name}" uploaded.`;
            // Add details based on response structure
            if (response && typeof response.products_added !== 'undefined') {
                successMsg += ` ${response.products_added} new products added, ${response.products_skipped} existing products skipped.`;
            } else if (response && typeof response.sales_transactions_logged !== 'undefined') {
                 // Check if stock_updated_for_products exists and is an array before joining
                 const updatedProducts = (response.stock_updated_for_products && Array.isArray(response.stock_updated_for_products))
                    ? response.stock_updated_for_products.join(', ')
                    : 'None';
                successMsg += ` ${response.sales_transactions_logged} sales logged. Updated stock for: ${updatedProducts}`;

            } else if (response) {
                 successMsg += ` Server response: ${JSON.stringify(response)}`; // Fallback for other responses
            }
            this.showMessage(successMsg, false);
            event.target.reset();
        } catch (error) {
            this.showLoader(false);
            this.showMessage(`Upload Failed: ${error.message}`, true);
        }
    },

    async handleAddBatch(event) {
        event.preventDefault();
        this.showLoader(true);

        const productIdInput = document.getElementById('batch-product-id');
        const quantityInput = document.getElementById('batch-quantity');
        const expiryInput = document.getElementById('batch-expiry');

        const batch = {
            product_id: parseInt(productIdInput.value),
            quantity: parseInt(quantityInput.value),
            expiry_date: expiryInput.value
        };

        if (isNaN(batch.product_id) || isNaN(batch.quantity) || !batch.expiry_date) {
            this.showMessage('Please fill in all fields correctly (Product ID, Quantity, Expiry Date).', true);
            this.showLoader(false);
            return;
        }
        if (batch.quantity < 0) {
             this.showMessage('Quantity cannot be negative.', true);
            this.showLoader(false);
            return;
        }
         if (!/^\d{4}-\d{2}-\d{2}$/.test(batch.expiry_date)) {
             this.showMessage('Expiry Date must be in YYYY-MM-DD format.', true);
             this.showLoader(false);
             return;
         }

        try {
            const response = await this.apiFetch('/stock/add_batch/', {
                method: 'POST',
                body: JSON.stringify(batch)
            });

            this.showLoader(false);
            // Assuming response directly is the created batch object
            this.showMessage(`Success: Batch for product ${response.product_id} added.`, false);
            event.target.reset();
        } catch (error) {
            this.showLoader(false);
            this.showMessage(`Failed to Add Batch: ${error.message}`, true);
        }
    },

    async handleBulkAdd(event) {
        event.preventDefault();
        this.showLoader(true);

        const jsonInput = this.elements.bulkBatchJsonInput.value;
        let batches;
        try {
             if (!jsonInput.trim()) throw new Error("JSON input cannot be empty.");
            batches = JSON.parse(jsonInput);
            if (!Array.isArray(batches)) throw new Error('Input must be a valid JSON array.');
            if (batches.length === 0) throw new Error("JSON array cannot be empty.");

            batches.forEach((batch, index) => {
                const itemNum = index + 1;
                if (typeof batch.product_id !== 'number') throw new Error(`Batch item ${itemNum}: 'product_id' must be a number.`);
                if (typeof batch.quantity !== 'number' || batch.quantity < 0) throw new Error(`Batch item ${itemNum}: 'quantity' must be a non-negative number.`);
                if (typeof batch.expiry_date !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(batch.expiry_date)) throw new Error(`Batch item ${itemNum}: 'expiry_date' must be a string in YYYY-MM-DD format.`);
            });
        } catch (parseError) {
            this.showLoader(false);
            this.showMessage(`Invalid Input: ${parseError.message}`, true);
            return;
        }

        try {
            const response = await this.apiFetch('/stock/add_batch_bulk/', {
                method: 'POST',
                body: JSON.stringify(batches)
            });

            this.showLoader(false);
             // Use the more detailed response from the backend
            const updatedProductsList = (response.products_updated && Array.isArray(response.products_updated))
                ? response.products_updated.join(', ')
                : 'None';
            this.showMessage(`Success: ${response.batches_added} batches added. Products updated: ${updatedProductsList}`, false);
            event.target.reset();
        } catch (error) {
            this.showLoader(false);
            this.showMessage(`Failed to Add Bulk Batches: ${error.message}`, true);
        }
    },

     async fetchDashboard() {
        // Prevent multiple fetches if already loading
        if (this.isLoading) {
            console.log("Dashboard fetch already in progress.");
            return;
        }
        
        // Ensure we are on the dashboard page before fetching
        if (this.currentMainPage !== 'dashboard') {
             console.log("Not on dashboard page, skipping fetch.");
             return;
        }

        this.showLoader(true);
        this.elements.dashboardTableBody.innerHTML = '<tr><td colspan="6" class="px-6 py-12 text-center text-gray-500">Loading report...</td></tr>';

        try {
            const data = await this.apiFetch('/dashboard/');
            this.dashboardData = Array.isArray(data) ? data : [];
            this.renderDashboardTable();
        } catch (error) {
            // Error handling is now done inside apiFetch or fetchCurrentUser which call handleLogout
            // Only update table if not logged out
            if (this.currentPage === 'mainApp') {
                 console.error(`Failed to load dashboard: ${error.message}`);
                 this.elements.dashboardTableBody.innerHTML = '<tr><td colspan="6" class="px-6 py-12 text-center text-red-500">Error loading data. Please try again or check connection.</td></tr>';
            }
        } finally {
             this.showLoader(false); // Ensure loader is always hidden
        }
    },


    // --- UI Rendering ---

    renderDashboardTable() {
        const tbody = this.elements.dashboardTableBody;
        tbody.innerHTML = ''; // Clear existing data

        if (!this.dashboardData || this.dashboardData.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-12 text-center text-muted-text">No items currently require attention based on expiry dates.</td></tr>';
            return;
        }

        this.dashboardData.forEach(item => {
            const row = document.createElement('tr');
            row.classList.add('hover:bg-secondary', 'transition-colors', 'duration-150');
            const statusBadgeClass = this.getStatusBadgeClass(item.status);
            const daysLeftClass = (item.days_to_expiry !== null && item.days_to_expiry <= 7) ? 'font-semibold text-red-600' : 'text-muted-text';


            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-primary">${item.name || 'N/A'}</div>
                    <div class="text-xs text-gray-500">ID: ${item.product_id}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="status-badge ${statusBadgeClass}">
                        ${item.status || 'OK'}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-dark-text text-right">${item.total_stock}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-muted-text text-right">${item.sales_last_week}</td>
                 <td class="px-6 py-4 whitespace-nowrap text-sm text-right ${daysLeftClass}">
                    ${item.days_to_expiry ?? 'N/A'}
                </td>

                <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold ${item.predicted_discount_percent > 0.01 ? 'text-red-600' : 'text-dark-text'} text-right">
                     ${item.predicted_discount_percent !== null && item.predicted_discount_percent !== undefined ? item.predicted_discount_percent.toFixed(2) + '%' : 'N/A'}

                </td>
            `;
            tbody.appendChild(row);
        });
    },

    getStatusBadgeClass(status) {
        switch (status) {
            case 'Urgent Discount!': return 'urgent-discount';
            case 'Wasted / Remove': return 'wasted';
            case 'Expiring Soon': return 'expiring-soon';
            case 'OK': default: return 'ok';
        }
    },

    // --- Utility Functions ---

    async apiFetch(endpoint, options = {}) {
        const defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        // Get token from storage for every request
        const currentAuthToken = localStorage.getItem('authToken');
        if (currentAuthToken) {
            defaultHeaders['Authorization'] = `Bearer ${currentAuthToken}`;
        } else if (!endpoint.includes('/token') && !endpoint.includes('/register/')) {
            // If no token and not trying to log in/register, log out immediately
            console.log("No token found for authenticated request. Logging out.");
            this.handleLogout(); // This will redirect to login
            // Throw an error to stop the current fetch attempt
            throw new Error('Authentication required. Redirecting to login.');
        }


        if (options.body instanceof FormData) {
            delete defaultHeaders['Content-Type']; // Let browser set Content-Type for FormData
        }

        const config = {
            ...options,
            headers: { ...defaultHeaders, ...options.headers }
        };

        try {
            const response = await fetch(endpoint, config);

            // Handle 401 Unauthorized specifically
            if (response.status === 401) {
                console.log("Received 401 Unauthorized. Logging out.");
                this.handleLogout(); // This redirects to login
                // Throw error to prevent further processing in the original caller
                throw new Error('Session expired or invalid. Please login again.');
            }

            // Check for other non-OK responses
            if (!response.ok) {
                let errorDetail = `HTTP error ${response.status}: ${response.statusText}`;
                try {
                    // Try to get more specific error detail from backend JSON response
                    const errorData = await response.json();
                    errorDetail = errorData.detail || errorDetail;
                } catch (jsonError) {
                    // If response is not JSON, try to get text
                    try {
                        const textError = await response.text();
                        errorDetail = textError || errorDetail; // Use text error if available
                    } catch (textError) { /* Ignore if text parsing also fails */ }
                }
                console.error(`API Fetch Error on ${endpoint}:`, errorDetail);
                throw new Error(errorDetail); // Throw the more specific error
            }

            // Handle successful responses
            if (response.status === 204) return null; // No content

            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                return await response.json(); // Parse JSON response
            } else {
                console.warn(`Received non-JSON response from ${endpoint}: ${contentType}`);
                return await response.text(); // Return text for non-JSON
            }

        } catch (networkError) {
             // Catch network errors (e.g., server down, CORS issues)
             console.error(`Network or Fetch error for ${endpoint}:`, networkError);
             // Provide a user-friendly network error message
             throw new Error(`Network error: Could not connect to the server. Please check your connection or try again later.`);
        }
    },


    showLoader(show) {
        this.elements.loadingSpinner.classList.toggle('hidden', !show);
    },

    showMessage(message, isError = false) {
         // Prevent showing modal if it's already visible
         if (!this.elements.messageModal.classList.contains('hidden')) {
             console.log("Modal already visible, skipping new message:", message);
             return;
         }

        this.elements.modalTitle.textContent = isError ? 'Error' : 'Success';
        this.elements.modalTitle.className = `text-xl font-bold ${isError ? 'text-red-600' : 'text-green-600'} mb-3`; // Use darker green
        this.elements.modalMessage.textContent = message;

        this.elements.messageModal.classList.remove('hidden');
        requestAnimationFrame(() => { // Ensure display:flex is applied before animation
             this.elements.messageModal.querySelector('.modal-content').classList.add('scale-100', 'opacity-100');
             this.elements.messageModal.querySelector('.fixed.inset-0').classList.add('opacity-60');
        });
    },

    closeModal() {
        // Start fade-out animations
        this.elements.messageModal.querySelector('.modal-content').classList.remove('scale-100', 'opacity-100');
        this.elements.messageModal.querySelector('.fixed.inset-0').classList.remove('opacity-60');

        // Wait for animation to finish before adding 'hidden'
        setTimeout(() => {
            this.elements.messageModal.classList.add('hidden');
            // Reset modal styles for next time
             this.elements.messageModal.querySelector('.modal-content').classList.remove('scale-95', 'opacity-0');

        }, 300); // Must match CSS transition duration
    }
};

// Initialize the app when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});