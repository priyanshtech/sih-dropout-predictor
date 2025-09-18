document.addEventListener('DOMContentLoaded', async () => {
    const API_BASE_URL = 'https://sih-dropout-predictor.onrender.com';
    const listDiv = document.getElementById('list');

    try {
        const response = await fetch(`${API_BASE_URL}/api/students`, { credentials: 'include' });
        if (response.status === 401) {
            window.location.href = '/frontend/login.html';
            return;
        }
        if (!response.ok) {
            throw new Error('Failed to fetch student data');
        }
        const students = await response.json();
        if (students.length === 0) {
            listDiv.innerHTML = '<p>No students found in the database.</p>';
        } else {
            listDiv.innerHTML = '<ul>' + students.map(s => `<li>${s.name} - ${s.class} (${s.risk_level} Risk)</li>`).join('') + '</ul>';
        }
    } catch (error) {
        listDiv.innerHTML = `<p style="color: red;">Error: Could not connect to backend. ${error.message}</p>`;
    }
});