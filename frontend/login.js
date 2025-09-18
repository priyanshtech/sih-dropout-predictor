document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const errorMessageDiv = document.getElementById('error-message');
    
    // --- FINAL: Your Live Backend URL ---
    const API_BASE_URL = 'https://sih-dropout-predictor.onrender.com';

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        errorMessageDiv.textContent = '';
        const username = usernameInput.value;
        const password = passwordInput.value;
        try {
            const response = await fetch(`${API_BASE_URL}/api/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ username, password }),
            });
            const data = await response.json();
            if (response.ok) {
                window.location.href = '/frontend/index.html';
            } else {
                throw new Error(data.error || 'Login failed.');
            }
        } catch (error) {
            errorMessageDiv.textContent = error.message;
        }
    });
});