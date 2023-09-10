  /*
  document.addEventListener("DOMContentLoaded", function() {
        var submitButton = document.querySelector("input[type='submit']");
        submitButton.addEventListener("click", function(event) {
       //     event.preventDefault(); // Prevent the default form submission

            // Get the password and confirm password fields
            var password = document.querySelector("input[name='password']").value;
            var confirm = document.querySelector("input[name='confirm']").value;

            // Check if the password fields match
            if (password !== confirm) {
                alert("Password and Confirm Password do not match.");
            } else {
                // Submit the form if the password fields match
                var form = document.querySelector("form");
                form.submit();
            }
        });
    });

*/
var Btn = document.getElementById('submit');

Btn.addEventListener("submit", function(event) {
    var password = document.querySelector("input[name='password']").value;
var confirm = document.querySelector("input[name='confirm']").value;
    
    if (password === "" || password.length < 8)
        event.preventDefault();
        alert("Password too weak")
    else if (password !== confirm) {
        event.preventDefault();
        alert("Passwords don't match")
    }
    else{
       // window.location.href = "/homepage"
    }
})