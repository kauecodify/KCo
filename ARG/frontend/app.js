// KCo/ARG - Aplicacao Frontend

async function checkApiStatus() {
    const statusElement = document.getElementById('api-status');
    
    try {
        const response = await fetch('http://localhost:8000/api/health');
        const data = await response.json();
        
        if (data.status === 'healthy') {
            statusElement.textContent = 'API: Healthy ✓';
            statusElement.style.color = 'green';
        } else {
            statusElement.textContent = 'API: Unhealthy ✗';
            statusElement.style.color = 'red';
        }
    } catch (error) {
        statusElement.textContent = 'API: Offline ✗';
        statusElement.style.color = 'red';
    }
}

// Verificar status ao carregar a pagina
document.addEventListener('DOMContentLoaded', checkApiStatus);
