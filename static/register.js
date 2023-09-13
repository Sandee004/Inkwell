function validateForm(event) {
            var password = document.getElementById("password").value;
            var confirmPassword = document.getElementById("confirm-password").value;

            if (password !== confirmPassword) {
                alert("Password and Confirm Password do not match.");
                event.preventDefault(); // Prevent form submission
                return false;
            }
}