// frontend/static/js/api/api.js

export function fetchAPI(url, options = {}) {
    const token = localStorage.getItem('token');
    options.headers = {
        ...options.headers,
        'Authorization': `Token ${token}`,
    };

    return fetch(url, options)
    .then(response => {
        if (!response.ok) {
            if (response.status === 401) {
                // Handle unauthorized access, e.g., by logging out the user
                window.dispatchEvent(new CustomEvent('logout'));
            }
            throw new Error('Network response was not ok');
        }
        if (response.status === 204) { // No Content
            return null;
        }
        return response.json();
    })
    .catch(error => {
        console.error(`Error fetching ${url}:`, error);
        // Optionally, display an error message to the user
        const mainContent = document.getElementById('main-content');
        if (mainContent) {
            mainContent.innerHTML = `<p style="color: red;">Failed to load data.</p>`;
        }
    });
}
