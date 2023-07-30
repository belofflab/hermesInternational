$("form[name='signup']").submit((e) => {
    e.preventDefault();
    var error_box = $('#signup_errorbox');
    var first_name = $('#signup_first_name').val();
    var last_name = $('#signup_last_name').val();
    var email = $('#signup_email').val();
    var password = $('#signup_password').val();
    var country = $('#country_selector').val();
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
            country: country,
            csrfmiddlewaretoken: csrf_token
        },
        method: 'POST',
        url: '/ajax/accounts/signup'
    }).then((response) => {
        if (response.status) {
            window.location.href = '/accounts/profile/'
        } else {
            error_box.text(response.message);
            $("#signup_but").removeAttr('disabled');
        }
    })

})

$(document).ready(function() {
    $('#notify').on('change', ':checkbox', function() {
      $.post('/ajax/accounts/profile', $('#notify').serialize(), function(data) {
      });
    });
}); 

$('#signup_password').on('input', (e) => {
    var strongRegex = new RegExp("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})");
    var mediumRegex = new RegExp("^(((?=.*[a-z])(?=.*[A-Z]))|((?=.*[a-z])(?=.*[0-9]))|((?=.*[A-Z])(?=.*[0-9])))(?=.{6,})");
    var password = $('#signup_password')

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
    var email = $('#signin_email').val();
    var password = $('#signin_password').val();

    $("#signin_but").attr('disabled', 'disabled');

    $.ajax({
        data: {
            email: email,
            password: password,
            csrfmiddlewaretoken: csrf_token
        },
        method: 'POST',
        url: '/ajax/accounts/login'
    }).then((response) => {
        if (response.status) {
            window.location.href = '/accounts/profile/';
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

$("form[name='buy_out']").submit((e) => {
    e.preventDefault();
    var error_box = $('#buy_form_errorbox');
    var name = $('#buy_form_name').val();
    var url = $('#buy_form_url').val();
    var track_number = $('#buy_form_track_number').val();
    var quantity = $('#buy_form_quantity').val();
    var price = $('#buy_form_price').val();
    var status = $("#buy_option_select option:selected").val();
    if (status === "BUYOUT") {
        $("#buyout_but").attr('disabled', 'disabled');
        $.ajax({
            data: {
                name: name,
                url: url,
                track_number: track_number,
                quantity: quantity,
                price: price,
                status: status,
                csrfmiddlewaretoken: csrf_token
            },
            method: 'POST',
            url: '/ajax/inbox/create'
        }).then((response) => {
            if (response.status) {
                window.location.href = window.location.origin + '/accounts/profile/inbox/';
            } else {
                error_box.text(response.message);
            }
        })
        return;
    }
    $("#buyout_but").attr('disabled', 'disabled');
        $.ajax({
            data: {
                name: name,
                url: url,
                track_number: track_number,
                quantity: quantity,
                price: price,
                status: status,
                csrfmiddlewaretoken: csrf_token
            },
            method: 'POST',
            url: '/ajax/inbox/create'
        }).then((response) => {
            if (response.status) {
                $('#purchaseAddModal').modal('hide');
                localStorage.setItem("purchaseToAddingAccountData", response.data)
                $('#addressAddModal').modal('show');
            } else {
                error_box.text(response.message);
                $("#buyout_but").removeAttr('disabled');
            }
        })


})


$("form[name='buy_out']").submit((e) => {
    e.preventDefault();
    var error_box = $('#buy_form_errorbox');
    var name = $('#buy_form_name').val();
    var url = $('#buy_form_url').val();
    var track_number = $('#buy_form_track_number').val();
    var quantity = $('#buy_form_quantity').val();
    var price = $('#buy_form_price').val();
    var status = $("#buy_option_select option:selected").val();
    if (status === "BUYOUT") {
        $("#buyout_but").attr('disabled', 'disabled');
        $.ajax({
            data: {
                name: name,
                url: url,
                track_number: track_number,
                quantity: quantity,
                price: price,
                status: status,
                csrfmiddlewaretoken: csrf_token
            },
            method: 'POST',
            url: '/ajax/inbox/create'
        }).then((response) => {
            if (response.status) {
                window.location.href = window.location.origin + '/accounts/profile/inbox/';
            } else {
                error_box.text(response.message);
            }
        })
        return;
    }
    $("#buyout_but").attr('disabled', 'disabled');
        $.ajax({
            data: {
                name: name,
                url: url,
                track_number: track_number,
                quantity: quantity,
                price: price,
                status: status,
                csrfmiddlewaretoken: csrf_token
            },
            method: 'POST',
            url: '/ajax/inbox/create'
        }).then((response) => {
            if (response.status) {
                $('#purchaseAddModal').modal('hide');
                localStorage.setItem("purchaseToAddingAccountData", response.data)
                $('#addressAddModal').modal('show');
            } else {
                error_box.text(response.message);
                $("#buyout_but").removeAttr('disabled');
            }
        })


})


$("form[name='address_inf']").submit((e) => {
    e.preventDefault();
    var purchase = localStorage.getItem("purchaseToAddingAccountData");
    // var first_name = $('#address_form_first_name').val();
    // var last_name = $('#address_form_last_name').val();
    // var sur_name = $('#address_form_sur_name').val();
    var phone = $('#address_form_phone').val();
    var city = $('#address_form_city').val();
    var street = $('#address_form_street').val();
    var state = $('#address_form_state').val();
    var postal_code = $('#address_form_postal_code').val();
    var country = $('#country_selector_2').val();

    var options = $(".address_form_option");

    var sortedOptions = [];

    options.each((option) => {
        if($(options[option]).prop('checked')) {
            sortedOptions.push(options[option].dataset.option)
        }
    })

    $("#address_inf_but").attr('disabled', 'disabled');

    $.ajax({
        data: {
            purchase: purchase,
            phone: phone,
            city: city,
            street: street,
            state: state,
            postal_code: postal_code,
            country: country,
            options: sortedOptions,
            csrfmiddlewaretoken: csrf_token
        },
        method: 'POST',
        url: '/ajax/account/data/create'
    }).then((response) => {
        if (response.status) {
            $('#addressAddModal').modal('hide');
            localStorage.setItem("purchaseToAddingAccountData", "")
            window.location.reload()
        } else {
            console.log(response)
        }
    })


})




$("form[name='edit_profile']").submit((e) => {
    e.preventDefault();
    var first_name = $('#edit_profile_form_firstname').val();
    var last_name = $('#edit_profile_form_lastname').val();
    var sur_name = $('#edit_profile_form_surname').val();
    var country = $('#country_selector_2').val();

    console.log(first_name, last_name, sur_name, country)

    $("#edit_profie_but").attr('disabled', 'disabled');

    $.ajax({
        data: {
            first_name: first_name,
            last_name: last_name,
            sur_name: sur_name,
            country: country,
            csrfmiddlewaretoken: csrf_token
        },
        method: 'POST',
        url: '/ajax/account/data/update'
    }).then((response) => {
        if (response.status) {
            $('#editProfileAddModal').modal('hide');
            window.location.reload()
        } else {
            console.log(response)
        }
    })


})