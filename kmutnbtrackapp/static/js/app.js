const navSlide = () =>{
    const burger = document.querySelector('.burger');
    const nav = document.querySelector('.upnav-link');
    const navLinks = document.querySelectorAll('.upnav-link li');
    //toggle
    burger.addEventListener('click',() => {
       nav.classList.toggle('upnav-active');
    //animation links
    navLinks.forEach((link,index)=>{
        if (link.style.animation){
            link.style.animation = '';
        } else {
            link.style.animation = `navLinkFade 0.5s ease forwards ${index / 7+0.5}s`;
        }
    });
    //Burger animation
        burger.classList.toggle('toggle');
});
}
navSlide();