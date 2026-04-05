// Navigation functionality for top navigation layout

document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const mobileToggle = document.querySelector('.mobile-nav-toggle');
    const navLinks = document.querySelector('.top-nav-links');
    
    if (mobileToggle && navLinks) {
        mobileToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            navLinks.classList.toggle('mobile-show');
            // Update icon
            const icon = mobileToggle.querySelector('i');
            if (navLinks.classList.contains('mobile-show')) {
                icon.classList.remove('bi-list');
                icon.classList.add('bi-x-lg');
            } else {
                icon.classList.remove('bi-x-lg');
                icon.classList.add('bi-list');
            }
        });
    }
    
    // Close mobile nav when clicking outside
    document.addEventListener('click', function(e) {
        if (navLinks && navLinks.classList.contains('mobile-show')) {
            if (!navLinks.contains(e.target) && (!mobileToggle || !mobileToggle.contains(e.target))) {
                navLinks.classList.remove('mobile-show');
                if (mobileToggle) {
                    const icon = mobileToggle.querySelector('i');
                    icon.classList.remove('bi-x-lg');
                    icon.classList.add('bi-list');
                }
            }
        }
    });
    
    // Close mobile nav when window resizes to desktop
    window.addEventListener('resize', function() {
        if (window.innerWidth > 991 && navLinks) {
            navLinks.classList.remove('mobile-show');
            if (mobileToggle) {
                const icon = mobileToggle.querySelector('i');
                icon.classList.remove('bi-x-lg');
                icon.classList.add('bi-list');
            }
        }
    });
    
    // Close dropdowns when clicking outside on desktop
    document.addEventListener('click', function(e) {
        if (window.innerWidth > 991) {
            const dropdowns = document.querySelectorAll('.nav-module-dropdown.show');
            dropdowns.forEach(function(dropdown) {
                if (!dropdown.contains(e.target)) {
                    dropdown.classList.remove('show');
                }
            });
        }
    });
    
    // Search input handling
    const searchInput = document.getElementById('global-search');
    const searchResults = document.getElementById('search-results');
    const searchWrapper = document.querySelector('.nav-search-wrapper');
    
    if (searchInput && searchResults) {
        searchInput.addEventListener('focus', function() {
            this.parentElement.classList.add('search-focused');
        });
        
        searchInput.addEventListener('blur', function() {
            setTimeout(() => {
                if (searchResults) {
                    searchResults.style.display = 'none';
                }
            }, 200);
        });
        
        // Show results when HTMX loads them
        searchInput.addEventListener('input', function() {
            if (this.value.length > 0 && searchResults) {
                setTimeout(() => {
                    if (searchResults.innerHTML.trim()) {
                        searchResults.style.display = 'block';
                    }
                }, 600);
            }
        });
    }
    
    // Highlight active navigation item based on current path
    const currentPath = window.location.pathname;
    const navLinksItems = document.querySelectorAll('.nav-module-link');
    
    navLinksItems.forEach(function(link) {
        const href = link.getAttribute('href');
        if (href && (currentPath === href || currentPath.startsWith(href + '/'))) {
            link.classList.add('active');
        }
    });
    
    // Submenu hover for desktop
    const submenuItems = document.querySelectorAll('.dropdown-submenu');
    submenuItems.forEach(function(submenu) {
        submenu.addEventListener('mouseenter', function() {
            if (window.innerWidth > 991) {
                const dropdownMenu = this.querySelector('.dropdown-menu');
                if (dropdownMenu) {
                    dropdownMenu.style.display = 'block';
                }
            }
        });
        
        submenu.addEventListener('mouseleave', function() {
            if (window.innerWidth > 991) {
                const dropdownMenu = this.querySelector('.dropdown-menu');
                if (dropdownMenu) {
                    dropdownMenu.style.display = 'none';
                }
            }
        });
    });
});

// Prevent dropdown close on click inside
document.addEventListener('click', function(e) {
    const dropdownMenus = document.querySelectorAll('.dropdown-menu-nav, .dropdown-menu-user');
    dropdownMenus.forEach(function(menu) {
        if (menu.contains(e.target)) {
            e.stopPropagation();
        }
    });
});
