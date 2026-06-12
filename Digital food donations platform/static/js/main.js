// Toast Notification System
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} fade-in`;
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.style.minWidth = '300px';
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Countdown Timer for Expiry
function updateCountdowns() {
    const countdowns = document.querySelectorAll('[data-expiry]');

    countdowns.forEach(element => {
        const expiryTime = new Date(element.dataset.expiry).getTime();
        const now = new Date().getTime();
        const diff = expiryTime - now;

        if (diff < 0) {
            element.textContent = 'Expired';
            element.className = 'badge badge-danger';
            return;
        }

        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

        if (hours > 24) {
            const days = Math.floor(hours / 24);
            element.textContent = `${days} day${days > 1 ? 's' : ''} remaining`;
            element.className = 'badge badge-success';
        } else if (hours > 3) {
            element.textContent = `${hours} hour${hours > 1 ? 's' : ''} remaining`;
            element.className = 'badge badge-info';
        } else {
            element.textContent = `${hours}h ${minutes}m remaining`;
            element.className = 'badge badge-warning';
        }
    });
}

// Form Validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.style.borderColor = 'var(--danger)';
        } else {
            input.style.borderColor = 'var(--glass-border)';
        }
    });

    return isValid;
}

// Search and Filter
function filterTable(searchInputId, tableId) {
    const input = document.getElementById(searchInputId);
    const table = document.getElementById(tableId);

    if (!input || !table) return;

    const filter = input.value.toLowerCase();
    const rows = table.getElementsByTagName('tr');

    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        const text = row.textContent.toLowerCase();

        if (text.includes(filter)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    }
}

// Confirm Action
function confirmAction(message) {
    return confirm(message);
}

// Auto-update countdowns every minute
if (document.querySelectorAll('[data-expiry]').length > 0) {
    updateCountdowns();
    setInterval(updateCountdowns, 60000);
}

// Phone number formatting
function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length > 10) {
        value = value.slice(0, 10);
    }
    input.value = value;
}

// Initialize tooltips and other interactive elements
document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Add smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});
