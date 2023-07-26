$("form[name='signup']").submit((e) => {
    e.preventDefault();
    var error_box = $('#signup_errorbox');
    var first_name = $('#signup_first_name').val();
    var last_name = $('#signup_last_name').val();
    var email =  $('#signup_email').val();
    var password =  $('#signup_password').val();
    var country =  $('#country_selector').val();
    var mediumRegex = new RegExp("^(((?=.*[a-z])(?=.*[A-Z]))|((?=.*[a-z])(?=.*[0-9]))|((?=.*[A-Z])(?=.*[0-9])))(?=.{6,})");
    if (!mediumRegex.test(password)) {
        return;
    }
    $("#signup_but").attr('disabled', 'disabled');
    $.ajax({
        data: {
            first_name: first_name,
            last_name: last_name,
            email: email,
            password: password,
            country:country,
            csrfmiddlewaretoken: csrf_token
        },
        method: 'POST',
        url: '/en/accounts/signup/'
    }).then((response) => {
        if (response.status) {
            window.location.href = 'accounts/profile/'
        } else {
            error_box.text(response.message);
            $("#signup_but").removeAttr('disabled');
        }
    })

})

$('#signup_password').on('input', (e) => {
    var strongRegex = new RegExp("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})");
    var mediumRegex = new RegExp("^(((?=.*[a-z])(?=.*[A-Z]))|((?=.*[a-z])(?=.*[0-9]))|((?=.*[A-Z])(?=.*[0-9])))(?=.{6,})");
    var password =  $('#signup_password')

    if (strongRegex.test(password.val())) {
        password.css('color', 'green')
    } else if (mediumRegex.test(password.val())) {
        password.css('color', 'orange')
    } else {
        password.css('color', 'red')
    }

})


$("form[name='signin']").submit((e) => {
    e.preventDefault();
    var errorbox = $('#signin_errorbox')
    var email =  $('#signin_email').val();
    var password =  $('#signin_password').val();

    $("#signin_but").attr('disabled', 'disabled');

    $.ajax({
        data: {
            email: email,
            password: password,
            csrfmiddlewaretoken: csrf_token
        },
        method: 'POST',
        url: '/en/accounts/login/'
    }).then((response) => {
        if (response.status) {
            window.location.href = 'accounts/profile/';
        } else {
            errorbox.text(response.message);
            $("#signin_but").removeAttr('disabled');
        }
    })

})



$("#or_signin").on('click', (e) => {
    $('#signupModal').modal('hide');
    $('#signinModal').modal('show');
})

$("#or_signup").on('click', (e) => {
    $('#signinModal').modal('hide');
    $('#signupModal').modal('show');
})