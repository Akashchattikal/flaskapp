
const dialog = document.getElementById("dialog_ord");

function showDialog() {
    dialog.show();
    selectElement = document.querySelector('#taco');
    output = selectElement.value;
    document.querySelector('.output').textContent = output;
}

function closeDialog() {
    dialog.close();
}
