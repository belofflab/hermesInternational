const recaptchaSiteKey = '6LdIh4UnAAAAAI3ta-SSP_smWqV2fJeHJ0wkQ9py';

$(document).ready(function () {
    $("#user_warehouse").submit(function (event) {
        event.preventDefault(); // Prevent form submission

        var phone = $('#warehouse_form_phone').val();
        var city = $('#warehouse_form_city').val();
        var street = $('#warehouse_form_street').val();
        var state = $('#warehouse_form_state').val();
        var postal_code = $('#warehouse_form_postal_code').val();

        // $('#warehouse_but').attr('disabled', 'disabled');

        // $.ajax({
        //     url: "/ajax/accounts/profile/warehouses/create", // Replace 'your-ajax-url' with your actual AJAX URL
        //     type: "POST",
        //     data: {
        //         phone: phone,
        //         city: city,
        //         street: street,
        //         state: state,
        //         postal_code: postal_code,
        //         csrfmiddlewaretoken: csrf_token
        //     },
        //     success: function (response) {
        //         $('#warehouseAddModal').modal('hide');
        //         window.location.reload();
        //     },
        //     error: function (xhr, errmsg, err) {
        //         console.log(xhr.status + ": " + xhr.responseText);
        //         $("#warehouse_but").removeAttr('disabled');
        //     }
        // });
        $('#warehouseAddModal').modal('hide');
    });
});


$('#signinModal').on('show.bs.modal', function (event) {
    if (user !== 'AnonymousUser') {
        window.location.href = '/accounts/profile/';
        $('#signinModal').modal('hide');
        return;
    }
    return;
});

$('#signupModal').on('show.bs.modal', function (event) {
    if (user !== 'AnonymousUser') {
        window.location.href = '/accounts/profile/';
        $('#signupModal').modal('hide');
        return;
    }
    return;
});

function toRegister() {

    $('#signupModal').modal('show');

}


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

    grecaptcha.enterprise.ready(function () {
        grecaptcha.enterprise.execute(recaptchaSiteKey, { action: 'signup' }).then(function (token) {
            // Append the reCAPTCHA token to your form data
            const form = document.querySelector('form[name="signup"]');
            const formData = new FormData(form);
            formData.append('recaptcha_token', token);


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
    })
})

$(document).ready(function () {
    $('#notify').on('change', ':checkbox', function () {
        $.post('/ajax/accounts/profile', $('#notify').serialize(), function (data) {
        });
    });
});

$('#signup_password').on('input', (e) => {
    var strongRegex = new RegExp("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})");
    var mediumRegex = new RegExp("^(((?=.*[a-z])(?=.*[A-Z]))|((?=.*[a-z])(?=.*[0-9]))|((?=.*[A-Z])(?=.*[0-9])))(?=.{6,})");
    var password = $('#signup_password')

    if (strongRegex.test(password.val())) {
        password.css('color', 'green');
    } else if (mediumRegex.test(password.val())) {
        password.css('color', 'orange');
    } else {
        password.css('color', 'red');
    }

})


$('#signup_first_name').on('keyup', function() {
    var inputValue = $(this).val();
    var filteredValue = inputValue.replace(/[^a-zA-Z]/g, ''); // Remove non-letter characters
    $(this).val(filteredValue);
  });

$('#signup_last_name').on('keyup', function() {
    var inputValue = $(this).val();
    var filteredValue = inputValue.replace(/[^a-zA-Z]/g, ''); // Remove non-letter characters
    $(this).val(filteredValue);
  });

  function validateOnlyNumberInput(inputElement) {
    // Get the current input value
    let inputValue = inputElement.value;
  
    // Remove any non-numeric characters except for periods (for floats)
    inputValue = inputValue.replace(/[^0-9.]/g, '');
  
    // Remove leading zeros
    inputValue = inputValue.replace(/^0+/g, '');
  
    // If there is more than one period, keep only the first one
    const periods = inputValue.split('.');
    if (periods.length > 2) {
        inputValue = periods[0] + '.' + periods.slice(1).join('');
    }
  
    // Update the input value with the sanitized content
    inputElement.value = inputValue;
}

function validateNumberInput(inputElement) {
    // Get the current input value
    let inputValue = inputElement.value;
  
    // Remove any non-numeric characters except for periods (for floats)
    inputValue = inputValue.replace(/[^0-9.]/g, '');
  
    // If there is more than one period, keep only the first one
    if (inputValue.indexOf('.') !== inputValue.lastIndexOf('.')) {
      inputValue = inputValue.replace(/(.*\..*)\./g, '$1');
    }
  
    // Update the input value with the sanitized content
    inputElement.value = inputValue;
}


$("form[name='signin']").submit((e) => {
    e.preventDefault();
    var errorbox = $('#signin_errorbox')
    var email = $('#signin_email').val();
    var password = $('#signin_password').val();

    grecaptcha.enterprise.ready(function () {
        grecaptcha.enterprise.execute(recaptchaSiteKey, { action: 'signup' }).then(function (token) {
            // Append the reCAPTCHA token to your form data
            const form = document.querySelector('form[name="signup"]');
            const formData = new FormData(form);
            formData.append('recaptcha_token', token);
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
    var id = $('#buy_form_id').val();
    var name = $('#buy_form_name').val();
    var url = $('#buy_form_url').val();
    var track_number = $('#buy_form_track_number').val();
    var quantity = $('#buy_form_quantity').val();
    var price = $('#buy_form_price').val();
    var status = $("#buy_option_select option:selected").val();
    if (!id.length > 0) { id = null }
    if (status === "BUYOUT") {
        $("#buyout_but").attr('disabled', 'disabled');
        $.ajax({
            data: {
                id: parseInt(id),
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
                window.location.href = '/accounts/profile/inbox/';
            } else {
                error_box.text(response.message);
                $("#buyout_but").removeAttr('disabled');
            }
        })
        return;
    }
    $("#buyout_but").attr('disabled', 'disabled');
    $.ajax({
        data: {
            id: parseInt(id),
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
            $("#buyout_but").removeAttr('disabled');
        } else {
            error_box.text(response.message);
            $("#buyout_but").removeAttr('disabled');
            $("form[name='buy_out']").reset()
        }
    })

})


$("form[name='address_inf']").submit((e) => {
    e.preventDefault();
    var purchase = localStorage.getItem("purchaseToAddingAccountData");
    var id = $('#address_form_id').val();
    // var first_name = $('#address_form_first_name').val();
    // var last_name = $('#address_form_last_name').val();
    // var sur_name = $('#address_form_sur_name').val();
    var phone = $('#address_form_phone').val();
    var city = $('#address_form_city').val();
    var street = $('#address_form_street').val();
    var state = $('#address_form_state').val();
    var postal_code = $('#address_form_postal_code').val();
    var country = $('#country_selector_2').val();
    var deliveryMethod = $("#address_form_delivery_method").val();

    var options = $(".address_form_option");

    var sortedOptions = [];

    options.each((option) => {
        if ($(options[option]).prop('checked')) {
            sortedOptions.push(options[option].dataset.option)
        }
    })

    $("#address_inf_but").attr('disabled', 'disabled');

    $.ajax({
        data: {
            id: id,
            purchase: purchase,
            phone: phone,
            city: city,
            street: street,
            state: state,
            postal_code: postal_code,
            country: country,
            deliveryMethod: deliveryMethod,
            options: sortedOptions,
            csrfmiddlewaretoken: csrf_token
        },
        method: 'POST',
        url: '/ajax/account/data/create'
    }).then((response) => {
        if (response.status) {
            $('#addressAddModal').modal('hide');
            localStorage.setItem("purchaseToAddingAccountData", "")
            window.location.href = '/accounts/profile/packages/'
        } else {
            console.log(response)
            $("#address_inf_but").removeAttr('disabled');
            $("form[name='address_inf']").reset()
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
            $("#edit_profie_but").removeAttr('disabled');
        }
    })


})




function toForwarding(purchaseId) {
    console.log(purchaseId)
    localStorage.setItem("purchaseToAddingAccountData", purchaseId);
    $('#addressAddModal').modal('show');
}

function toBuyout(purchaseId) {
    $.ajax({
        data: {
            purchase: parseInt(purchaseId),
            status: "BUYOUT",
            csrfmiddlewaretoken: csrf_token
        },
        method: 'POST',
        url: '/ajax/purchase/status/update'
    }).then((response) => {
        if (response.status) {
            window.location.reload()
        } else {
            console.log(response)
        }
    })
}

function toAcceptance(purchaseId) {
    $.ajax({
        data: {
            purchase: parseInt(purchaseId),
            status: "ACCEPTANCE",
            csrfmiddlewaretoken: csrf_token
        },
        method: 'POST',
        url: '/ajax/purchase/status/update'
    }).then((response) => {
        if (response.status) {
            // window.location.href = 'accounts/profile/inbox'
            window.location.reload()
        } else {
            console.log(response)
        }
    })
}



function deleteUserWarehouse(warehouseId) {
    $.ajax({
        data: {
            warehouse: parseInt(warehouseId),
            csrfmiddlewaretoken: csrf_token
        },
        method: 'POST',
        url: '/ajax/accounts/profile/warehouses/delete',
    }).then((response) => {
        if (response.status) {
            window.location.reload()
        } else {
            console.log(response)
        }
    })
}


function purchaseToForm(purchase) {
    $('#buy_form_id').val(purchase.id);
    $('#buy_form_name').val(purchase.name);
    $('#buy_form_url').val(purchase.link);
    $('#buy_form_track_number').val(purchase.tracking_number);
    $('#buy_form_quantity').val(purchase.quantity);
    $('#buy_form_price').val(purchase.price);
    $('#buy_option_select').val(purchase.status);
}

function addressToForm(address) {
    console.log(address)
    address.options.forEach(option => {
        $("#" + option).prop("checked", 1);
    });
    $('#address_form_delivery_method').val(address.delivery_method)
    $('#address_form_id').val(address.id);
    $('#address_form_street').val(address.street);
    $('#address_form_city').val(address.city);
    $('#country_selector_2').val(address.country);
    $('#address_form_state').val(address.state);
    $('#address_form_phone').val(address.phone);
    $('#address_form_postal_code').val(address.postal_code);
    
}

function updatePurchaseData(purchaseId, addressId) {
    var requestData = {
        purchaseId: parseInt(purchaseId),
        csrfmiddlewaretoken: csrf_token
    };

    if (addressId.length > 0) {
        requestData.addressId = Number(addressId);
    }

    $.ajax({
        data: requestData,
        method: 'POST',
        url: '/ajax/accounts/profile/purchases/get',
    }).then((response) => {
        if (response.status) {
            console.log(response)
            purchaseToForm(response.purchase);
            if (addressId.length > 0) {
                var address = response.address
                address.delivery_method = response.purchase.delivery_method
                address.options = response.purchase.options
                addressToForm(response.address);
            }
            $('#purchaseAddModal').modal('show');
        }
    }).catch((response) => {
        console.log(response)
    });
}


$("#profile-image").on("click", function() {
    $("#profile-image-input").click();
  });

$('#profile-image-input').change(function(e) {
var file = e.target.files[0];
if (file && file.type.startsWith('image/')) {
    var formData = new FormData();
    formData.append('profile_image', file);
    formData.append('csrfmiddlewaretoken', csrf_token);

    $.ajax({
    type: 'POST',
    url: '/ajax/accounts/profile/avatar', // Replace with the actual URL for image upload
    data: formData,
    processData: false,
    contentType: false,
    success: function(response) {
        $('#profile-image').attr('src', response.image_url);
    },
    error: function(error) {
        console.log(error);
    }
    });
}
});