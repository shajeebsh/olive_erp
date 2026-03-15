document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.querySelector('.sidebar-container');
    const toggler = document.querySelector('[data-bs-target="#sidebarMenu"]');

    if (toggler) {
        toggler.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
        });
    }

    // Toggle Submenus
    const parentLinks = document.querySelectorAll('.sidebar-nav .nav-item > a');
    parentLinks.forEach(link => {
        const submenu = link.nextElementSibling;
        if (submenu && submenu.classList.contains('submenu')) {
            link.addEventListener('click', function(e) {
                // If it's a parent link with a submenu, toggle it
                e.preventDefault();
                submenu.classList.toggle('show');
                
                // Toggle rotation on chevron if exists
                const chevron = this.querySelector('.bi-chevron-down');
                if (chevron) {
                    chevron.style.transform = submenu.classList.contains('show') ? 'rotate(180deg)' : 'rotate(0deg)';
                }
            });
        }
    });

    // Auto-expand menu if current path matches a sub-item
    const activeSubLink = document.querySelector('.submenu .nav-link.active');
    if (activeSubLink) {
        const parentSubmenu = activeSubLink.closest('.submenu');
        if (parentSubmenu) {
            parentSubmenu.classList.add('show');
            const parentLink = parentSubmenu.previousElementSibling;
            const chevron = parentLink.querySelector('.bi-chevron-down');
            if (chevron) chevron.style.transform = 'rotate(180deg)';
        }
    }
});

