const navLinks = document.querySelectorAll('.nav_link');

navLinks.forEach(navLink => {
    navLink.addEventListener('click', () => {
        document.querySelector('.btn')?.classList.remove('btn');
        navLink.classList.add('btn');
    });
});
