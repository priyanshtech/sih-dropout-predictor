document.addEventListener('DOMContentLoaded', async () => {

    // --- FINAL: Your Live Backend URL ---
    const API_BASE_URL = 'https://sih-dropout-predictor.onrender.com'; // <-- PASTE YOUR URL HERE

    // --- API Function ---
    async function apiGet(endpoint) {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, { credentials: 'include' });
        if (response.status === 401) window.location.href = '/frontend/login.html';
        if (!response.ok) throw new Error(`API GET Error: ${response.status}`);
        return response.json();
    }

    // --- Chart Creation Functions ---
    function createRiskByClassChart(stats) {
        const ctx = document.getElementById('riskByClassChart').getContext('2d');
        const labels = Object.keys(stats.risk_by_class);
        const data = Object.values(stats.risk_by_class);

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'At-Risk Students',
                    data: data,
                    backgroundColor: 'rgba(139, 92, 246, 0.6)',
                    borderColor: 'rgba(139, 92, 246, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: { beginAtZero: true, ticks: { color: '#9ca3af', stepSize: 1 }, grid: { color: '#4b5563' } },
                    x: { ticks: { color: '#9ca3af' }, grid: { display: false } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    // --- Main Initialization ---
    async function init() {
        try {
            const stats = await apiGet('/api/dashboard-stats');
            document.getElementById('total-students-stat').textContent = stats.total_students;
            document.getElementById('high-risk-stat').textContent = stats.high_risk_count;
            document.getElementById('medium-risk-stat').textContent = stats.medium_risk_count;
            createRiskByClassChart(stats);
        } catch (error) {
            console.error("Failed to load dashboard data:", error);
            document.body.innerHTML = '<h1>Error loading data. Please ensure you are logged in as an admin.</h1>';
        }
    }

    init();
});