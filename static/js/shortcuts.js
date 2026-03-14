document.addEventListener('keydown', function(event) {
    // Alt + G: Focus Go To Search
    if (event.altKey && event.key === 'g') {
        event.preventDefault();
        const searchInput = document.getElementById('global-search');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // Ctrl + /: Help / Shortcuts list
    if (event.ctrlKey && event.key === '/') {
        event.preventDefault();
        alert('Keyboard Shortcuts:\nAlt+G: Focus Search\nAlt+N: New Invoice\nAlt+A: Add Account');
    }

    // Alt + N: New Invoice
    if (event.altKey && event.key === 'n') {
        window.location.href = '/finance/invoices/create/';
    }

    // Alt + A: New Account
    if (event.altKey && event.key === 'a') {
        window.location.href = '/finance/accounts/create/';
    }
});
