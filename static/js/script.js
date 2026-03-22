// Small client-side helpers for the IRIS Job Portal.
document.addEventListener("DOMContentLoaded", () => {
    const flashes = document.querySelectorAll(".flash");
    flashes.forEach((flash, index) => {
        flash.style.opacity = "0";
        flash.style.transform = "translateY(10px)";
        setTimeout(() => {
            flash.style.transition = "opacity 0.3s ease, transform 0.3s ease";
            flash.style.opacity = "1";
            flash.style.transform = "translateY(0)";
        }, 120 * index);
    });
});
