document.addEventListener("DOMContentLoaded", function () {
    const menuItems = document.querySelectorAll(".menu-item");
    
    // Get last active menu from localStorage
    let activeMenu = localStorage.getItem("activeMenu");
    if (!activeMenu) {
        activeMenu = "/dashboard/"; // Default to dashboard if no menu is saved
        localStorage.setItem("activeMenu", activeMenu);
    }
    
    menuItems.forEach(item => item.classList.remove("activeMenu"));
    const activeElement = document.querySelector(`.menu-item[href='${activeMenu}']`);
    if (activeElement) {
        activeElement.classList.add("activeMenu");
    }
    
    // Add click event to menu items
    menuItems.forEach(item => {
        item.addEventListener("click", function () {
            menuItems.forEach(el => el.classList.remove("activeMenu")); // Remove active class from all
            this.classList.add("activeMenu"); // Add active class to clicked item
            localStorage.setItem("activeMenu", this.getAttribute("href")); // Save in localStorage
        });
    });
});