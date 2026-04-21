// Optional: Add interactive functionality here

// Example: Highlight rows on hover
document.addEventListener('DOMContentLoaded', function() {
    const rows = document.querySelectorAll('table tr');
    rows.forEach(row => {
        row.addEventListener('mouseenter', () => {
            row.style.backgroundColor = '#f0f8ff';
        });
        row.addEventListener('mouseleave', () => {
            row.style.backgroundColor = '';
        });
    });
});