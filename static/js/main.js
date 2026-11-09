
document.addEventListener("DOMContentLoaded", function () {
    // Mobile navigation menu
    const menuButton = document.getElementById("mobileMenuBtn");
    const navigation = document.getElementById("navLinks");

    if (menuButton && navigation) {
        menuButton.addEventListener("click", function () {
            const isOpen = navigation.classList.toggle("active");

            menuButton.setAttribute("aria-expanded", String(isOpen));
            menuButton.setAttribute(
                "aria-label",
                isOpen ? "Close navigation menu" : "Open navigation menu"
            );
        });

        navigation.querySelectorAll("a").forEach(function (link) {
            link.addEventListener("click", function () {
                navigation.classList.remove("active");
                menuButton.setAttribute("aria-expanded", "false");
            });
        });
    }

    // Prevent accidental duplicate form submissions
    document.querySelectorAll("form[data-disable-on-submit]").forEach(
        function (form) {
            form.addEventListener("submit", function () {
                const submitButton = form.querySelector(
                    'button[type="submit"]'
                );

                if (submitButton) {
                    submitButton.disabled = true;
                    submitButton.textContent = "Please wait...";
                }
            });
        }
    );
});
