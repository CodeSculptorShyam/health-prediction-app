document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".delete-form").forEach(function (form) {
        form.addEventListener("submit", function (event) {
            if (!window.confirm("Are you sure you want to delete this patient record?")) {
                event.preventDefault();
            }
        });
    });
});
