let pointer = document.querySelectorAll(".pointer")

pointer.forEach(function(e) {
    mouseMove(e);
})

function mouseMove(pointer) {
    document.addEventListener("mousemove", function(e) {
        pointerPos(e, pointer)
    })
}

function pointerPos(e, pointer) {
    mousePosX = e.x;
    mousePosY = e.y;
    pointer.style.left = mousePosX - (pointer.getBoundingClientRect().width * 0.5) + "px";
    pointer.style.top = mousePosY - (pointer.getBoundingClientRect().height * 0.5) + "px";


}