let mouseCursor = document.querySelector("mousemove", cursor);
let naviLinks = document.querySelectorAll(".nav-links li");

window.addEventListener('mousemove', cursor);

function cursor(e) {
    mouseCursor.style.top = e.pageY + "px";
    mouseCursor.style.left = e.pageX + "px";

}

naviLinks.forEach(link => {
    link.addEventListener('mouseleave', () => {
        mouseCursor.classList.remove('link-grow');
        link.classList.remove("hovered-link");
    });

    link.addEventListener('mouseover', () => {
        mouseCursor.classList.add('link-grow')
        link.classList.add("hovered-link");
    });
});