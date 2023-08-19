
$(document).ready(function() {
    if (window.history.replaceState) {
        window.history.replaceState(null, null, window.location.href);
    }

    function validateEmail(email) {
        var regex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
        return regex.test(email);
    }

    $("#registration-form").on("submit", function(event) {
        event.preventDefault();

        var username = $("#username").val();
        var email = $("#email").val();
        var pass1 = $("#pass1").val();
        var pass2 = $("#pass2").val();
        var phone_number = $("#phone_number").val();

        if (username === '') {
            swal("Oops!", "Username cannot be empty", "error");
        } else if (email === '') {
            swal("Oops!", "Email cannot be empty", "error");
        } else if (!validateEmail(email)) {
            swal("Oops!", "Put a valid email", "error");
        } else if (phone_number === '') {
            swal("Oops!", "Phone number cannot be empty", "error");
        } else if (pass1 === '') {
            swal("Oops!", "Password cannot be empty", "error");
        } else if (pass2 === '') {
            swal("Oops!", "Confirm Password cannot be empty", "error");
        } else if (pass1 !== pass2) {
            swal("Oops!", "Passwords do not match", "error");
        } else {
            // If all validations pass, submit the form
            this.submit();
        }
    });
});

