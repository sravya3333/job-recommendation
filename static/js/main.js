document.addEventListener("DOMContentLoaded", function () {
    // Mobile nav toggle
    const navToggle = document.getElementById("navToggle");
    const navLinks = document.querySelector(".nav-links");

    if (navToggle && navLinks) {
        navToggle.addEventListener("click", function () {
            navLinks.classList.toggle("open");
        });
    }

    // Auto-dismiss flash messages after a few seconds
    const flashes = document.querySelectorAll(".flash");
    flashes.forEach(function (flash) {
        setTimeout(function () {
            flash.style.transition = "opacity 0.5s ease";
            flash.style.opacity = "0";
            setTimeout(function () { flash.remove(); }, 500);
        }, 4000);
    });
});
