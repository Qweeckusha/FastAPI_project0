function toggleSidebar() {
    var sidebar = document.getElementById("sidebar");
    var mainContent = document.getElementById("main-content");

    if (sidebar.classList.contains("sidebar-open")) {
        sidebar.classList.remove("sidebar-open");
        mainContent.classList.remove("content-shift");
    } else {
        sidebar.classList.add("sidebar-open");
        mainContent.classList.add("content-shift");
    }
}
