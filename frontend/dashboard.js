document.addEventListener('DOMContentLoaded', async () => {
    // --- API Function (same as before, needed for auth) ---
    async function apiGet(endpoint) {
        const response = await fetch(`http://127.0.0.1:5000${endpoint}`, { credentials: 'include' });
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
                    y: { beginAtZero: true, ticks: { color: '#9ca3af' }, grid: { color: '#4b5563' } },
                    x: { ticks: { color: '#9ca3af' }, grid: { color: '#4b5563' } }
                },
                plugins: { legend: { labels: { color: '#9ca3af' } } }
            }
        });
    }

    // --- Main Initialization ---
    async function init() {
        try {
            const stats = await apiGet('/api/dashboard-stats');

            // Update simple stat cards
            document.getElementById('total-students-stat').textContent = stats.total_students;
            document.getElementById('high-risk-stat').textContent = stats.high_risk_count;
            document.getElementById('medium-risk-stat').textContent = stats.medium_risk_count;

            // Create the charts
            createRiskByClassChart(stats);

        } catch (error) {
            console.error("Failed to load dashboard data:", error);
            document.body.innerHTML = '<h1>Error loading data. Please ensure you are logged in as an admin.</h1>';
        }
    }

    init();
});