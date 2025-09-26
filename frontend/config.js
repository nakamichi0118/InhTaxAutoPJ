// Frontend Configuration
const config = {
    API_BASE_URL: window.location.hostname === 'localhost'
        ? 'http://localhost:8000/api'
        : 'https://inhtaxautopj-production.up.railway.app/api'
};