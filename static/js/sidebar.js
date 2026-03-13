document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.querySelector('.sidebar-container');
    const toggler = document.querySelector('[data-bs-target="#sidebarMenu"]');

    if (toggler) {
        toggler.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
        });
    }

    const navLinks = document.querySelectorAll('.sidebar-nav .nav-link');
    navLinks.forEach(link => {
        if (link.nextElementSibling && link.nextElementSibling.classList.contains('submenu')) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                this.nextElementSibling.classList.toggle('show');
            });
        }
    });
});
