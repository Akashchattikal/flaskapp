const navLinks = document.querySelectorAll('.nav_link');

let path = location.pathname; /* Gets URL of current page, stores in path */
let linkID;


if (path == "/") {
    linkID = "home"
} else if (path == "/about") {
    linkID = "about"
} else if (path == "/all_tacos") {
    linkID = "product"
} else if (path == "/order") {
    linkID = "order"
}

document.getElementById(linkID).style.fontWeight = "bold ";

