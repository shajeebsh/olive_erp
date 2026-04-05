// navigation.js — OliveERP
// Header interaction logic is now inlined in base.html for load-order reliability.
// This file is kept for any future supplemental navigation utilities.

document.addEventListener('DOMContentLoaded', function() {
    // Keyboard shortcut: Alt+G → focus global search
    document.addEventListener('keydown', function(e) {
        if (e.altKey && e.key === 'g') {
            e.preventDefault();
            var searchInput = document.getElementById('global-search');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
    });
});