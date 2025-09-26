// API Configuration
const config = {
    API_BASE_URL: window.location.hostname === 'localhost' 
        ? 'http://localhost:8000/api'
        : 'https://inhtaxautopj.up.railway.app/api'
};

// Export for use in app.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = config;
}