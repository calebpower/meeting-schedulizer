
function showDetail() {
  var x = document.getElementById("showDetail");
  if (x.style.display === "none") {
    x.style.display = "block";
  } else {
    x.style.display = "none";
  }
}


// $(document).ready(function(){
//   $(".dropdown, .btn-group").hover(function(){
//       var dropdownMenu = $(this).children(".dropdown-menu");
//       if(dropdownMenu.is(":visible")){
//           dropdownMenu.parent().toggleClass("open");
//       }
//   });
// });  

// $(document).ready(function(){
//   $(".dropdown, .btn-group").hover(function(){
//       var dropdownMenu = $(this).children(".dropdown-menu");
//       if(dropdownMenu.is(":visible")){
//           dropdownMenu.parent().toggleClass("open");
//       }
//   });
// });  

// $(document).ready(function(){
//   $('.dropdown-submenu a.test').on("click", function(e){
//     $(this).next('ul').toggle();
//     e.stopPropagation();
//     e.preventDefault();
//   });
// });