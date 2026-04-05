// Navigation functionality for two-row app shell

document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const mobileToggle = document.querySelector('.mobile-nav-toggle');
    const mainNav = document.querySelector('.main-nav');
    
    if (mobileToggle && mainNav) {
        mobileToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            mainNav.classList.toggle('mobile-show');
            // Update icon
            const icon = mobileToggle.querySelector('i');
            if (mainNav.classList.contains('mobile-show')) {
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
        if (mainNav && mainNav.classList.contains('mobile-show')) {
            if (!mainNav.contains(e.target) && (!mobileToggle || !mobileToggle.contains(e.target))) {
                mainNav.classList.remove('mobile-show');
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
        if (window.innerWidth > 991 && mainNav) {
            mainNav.classList.remove('mobile-show');
            if (mobileToggle) {
                const icon = mobileToggle.querySelector('i');
                icon.classList.remove('bi-x-lg');
                icon.classList.add('bi-list');
            }
        }
    });
    
    // Highlight active navigation item based on current path
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(function(link) {
        const href = link.getAttribute('href');
        if (href && href !== '#' && (currentPath === href || currentPath.startsWith(href + '/'))) {
            link.classList.add('active');
        }
    });
    
    // Submenu toggle on click for mobile
    const submenuToggles = document.querySelectorAll('.dropdown-submenu > .dropdown-toggle');
    submenuToggles.forEach(function(toggle) {
        toggle.addEventListener('click', function(e) {
            if (window.innerWidth <= 991) {
                e.preventDefault();
                e.stopPropagation();
                const submenu = this.parentElement;
                submenu.classList.toggle('show');
            }
        });
    });
});