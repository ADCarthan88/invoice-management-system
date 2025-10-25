// Invoice System JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Handle form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
    
    // Auto-refresh dashboard stats
    if (window.location.pathname === '/dashboard') {
        setInterval(refreshDashboardStats, 30000); // Refresh every 30 seconds
    }
});

async function handleFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';
    submitBtn.disabled = true;
    
    try {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        let url, method;
        if (form.id === 'client-form') {
            const isEdit = window.location.pathname.includes('/edit');
            const clientId = isEdit ? window.location.pathname.split('/')[2] : null;
            url = isEdit ? `/api/clients/${clientId}` : '/api/clients/';
            method = isEdit ? 'PUT' : 'POST';
        }
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showAlert('Success! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = '/clients';
            }, 1000);
        } else {
            const error = await response.json();
            showAlert(`Error: ${error.detail || 'Something went wrong'}`, 'danger');
        }
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
    } finally {
        // Restore button state
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

async function refreshDashboardStats() {
    try {
        const response = await fetch('/api/dashboard/stats');
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('total-clients').textContent = stats.clients;
            document.getElementById('total-invoices').textContent = stats.invoices;
            document.getElementById('total-revenue').textContent = `$${stats.revenue.toFixed(2)}`;
            document.getElementById('pending-payments').textContent = stats.pending;
        }
    } catch (error) {
        console.log('Failed to refresh stats:', error);
    }
}