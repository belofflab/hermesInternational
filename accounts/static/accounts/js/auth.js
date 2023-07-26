$("form[name='signup']").submit((e) => {
    e.preventDefault();
    var error_box = $('#signup_errorbox');
    var first_name = $('#signup_first_name').val();
    var last_name = $('#signup_last_name').val();
    var email =  $('#signup_email').val();
    var password =  $('#signup_password').val();
    var mediumRegex = new RegExp("^(((?=.*[a-z])(?=.*[A-Z]))|((?=.*[a-z])(?=.*[0-9]))|((?=.*[A-Z])(?=.*[0-9])))(?=.{6,})");
    if (!mediumRegex.test(password)) {
        return;
    }
    $.ajax({
        data: {
            first_name: first_name,
            last_name: last_name,
            email: email,
            password: password,
            csrfmiddlewaretoken: csrf_token
        },
        method: 'POST',
        url: 'accounts/signup/'
    }).then((response) => {
        if (response.status) {
            window.location.href = 'accounts/profile/'
        } else {
            error_box.text(response.message);
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

    $.ajax({
        data: {
            email: email,
            password: password,
            csrfmiddlewaretoken: csrf_token
        },
        method: 'POST',
        url: 'accounts/login/'
    }).then((response) => {
        if (response.status) {
            window.location.href = 'accounts/profile/';
        } else {
            errorbox.text(response.message);
        }
    })

})