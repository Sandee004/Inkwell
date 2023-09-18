function validateForm(event) {
            var password = document.getElementById("password").value;
            var confirm = document.getElementById("confirm-password").value;

            if (password !== confirm) {
                alert("Password and Confirm Password do not match.");
                event.preventDefault(); // Prevent form submission
                return false;
            }
    return true;
}
