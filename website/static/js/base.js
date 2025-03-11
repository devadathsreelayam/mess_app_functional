const toggler = document.querySelector('.navbar-toggler');
const navbarNav = document.querySelector('.navbar-nav');

toggler.addEventListener('click', () => {
    // Toggle the 'show' class to open/close the menu
    navbarNav.classList.toggle('show');
    
    // Toggle the 'state' attribute on the toggler button
    if (toggler.getAttribute('state') === 'checked') {
        toggler.removeAttribute('state'); // Remove 'checked' state
    } else {
        toggler.setAttribute('state', 'checked'); // Add 'checked' state
    }
});