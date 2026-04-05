// Navigation functionality for top navigation layout

document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const mobileToggle = document.querySelector('.mobile-nav-toggle');
    const navLinks = document.querySelector('.top-nav-links');
    
    if (mobileToggle && navLinks) {
        mobileToggle.addEventListener('click', function() {
            navLinks.classList.toggle('mobile-show');
        });
    }
    
    // Close mobile nav when clicking outside
    document.addEventListener('click', function(e) {
        if (navLinks && navLinks.classList.contains('mobile-show')) {
            if (!navLinks.contains(e.target) && !mobileToggle.contains(e.target)) {
                navLinks.classList.remove('mobile-show');
            }
        }
    });
    
    // Close mobile nav when window resizes to desktop
    window.addEventListener('resize', function() {
        if (window.innerWidth > 991 && navLinks) {
            navLinks.classList.remove('mobile-show');
        }
    });
    
    // Dropdown submenu positioning for desktop
    const dropdownSubmenus = document.querySelectorAll('.dropdown-submenu');
    dropdownSubmenus.forEach(function(submenu) {
        submenu.addEventListener('mouseenter', function() {
            if (window.innerWidth > 991) {
                const dropdownMenu = this.querySelector('.dropdown-menu');
                if (dropdownMenu) {
                    dropdownMenu.classList.add('show');
                }
            }
        });
        
        submenu.addEventListener('mouseleave', function() {
            if (window.innerWidth > 991) {
                const dropdownMenu = this.querySelector('.dropdown-menu');
                if (dropdownMenu) {
                    dropdownMenu.classList.remove('show');
                }
            }
        });
    });
    
    // Search input focus handling
    const searchInput = document.getElementById('global-search');
    const searchResults = document.getElementById('search-results');
    
    if (searchInput && searchResults) {
        searchInput.addEventListener('focus', function() {
            this.parentElement.classList.add('search-focused');
        });
        
        searchInput.addEventListener('blur', function() {
            // Delay to allow click on search results
            setTimeout(() => {
                this.parentElement.classList.remove('search-focused');
            }, 200);
        });
    }
    
    // Highlight active navigation item based on current path
    const currentPath = window.location.pathname;
    const navLinksItems = document.querySelectorAll('.nav-module-link');
    
    navLinksItems.forEach(function(link) {
        const href = link.getAttribute('href');
        if (href && currentPath === href) {
            link.classList.add('active');
        }
    });
    
    // Handle dropdown close on click outside
    document.addEventListener('click', function(e) {
        const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
        openDropdowns.forEach(function(dropdown) {
            if (!dropdown.contains(e.target) && !e.target.classList.contains('dropdown-toggle')) {
                dropdown.classList.remove('show');
            }
        });
    });
});
