const recaptchaSiteKey = '6LfOQH4nAAAAABxGt4chFCdBD8dJrQBHADpXr4yO';

$(document).ready(function () {
    const urlParams = new URLSearchParams(window.location.search);
    const nextPage = urlParams.get('next');
    if (nextPage) {
        $('#signupModal').modal('show');
    }
    $("#user_warehouse").submit(function (event) {
        event.preventDefault(); // Prevent form submission

        var phone = $('#warehouse_form_phone').val();
        var city = $('#warehouse_form_city').val();
        var street = $('#warehouse_form_street').val();
        var state = $('#warehouse_form_state').val();
        var postal_code = $('#warehouse_form_postal_code').val();

        $('#warehouse_but').attr('disabled', '');

        $.ajax({
            url: "/ajax/accounts/profile/warehouses/create",
            type: "POST",
            data: {
                phone: phone,
                city: city,
                street: street,
                state: state,
                postal_code: postal_code,
                csrfmiddlewaretoken: csrf_token
            },
            success: function (response) {
                if (response.status) {
                    $("#user_warehouse").hide();
                    $("#success_info").show();
                } else {
                    $("#user_warehouse").hide();
                    $("#error_info").show();
                }
                $('#warehouse_but').removeAttr('disabled');
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
                $("#user_warehouse").hide();
                $("#error_info").show();
                $("#warehouse_but").removeAttr('disabled');
            }
        });
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

// function toRegister() {
//     $('#signupModal').modal('show');

// }


$("form[name='signup']").submit((e) => {
    e.preventDefault();
    const urlParams = new URLSearchParams(window.location.search);
    const nextPage = urlParams.get('next');
    var error_box = $('#signup_errorbox');
    var first_name = $('#signup_first_name').val();
    var last_name = $('#signup_last_name').val();
    var email = $('#signup_email').val();
    var password = $('#signup_password').val();
    var telegram = $('#signup_telegram').val();
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
                    telegram: telegram,
                    country: country,
                    csrfmiddlewaretoken: csrf_token
                },
                method: 'POST',
                url: '/ajax/accounts/signup'
            }).then((response) => {
                if (response.status) {
                    if (nextPage) {
                        window.location.href = nextPage;
                    } else {
                        window.location.href = '/accounts/profile/'
                    }
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


$('#signup_first_name').on('keyup', function () {
    var inputValue = $(this).val();
    var filteredValue = inputValue.replace(/[^a-zA-Z]/g, ''); // Remove non-letter characters
    $(this).val(filteredValue);
});

$('#signup_last_name').on('keyup', function () {
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
    const urlParams = new URLSearchParams(window.location.search);
    const nextPage = urlParams.get('next');
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
                    if (nextPage) {
                        window.location.href = nextPage;
                    } else {
                        window.location.href = '/accounts/profile/'
                    }
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

$("#or_forget").on('click', (e) => {
    $('#signinModal').modal('hide');
    $('#passwordFullChangeModal').modal('show');
})

$("#or_signup").on('click', (e) => {
    $('#signinModal').modal('hide');
    $('#signupModal').modal('show');
})

$("form[name='change_password']").submit(function (event) {
    event.preventDefault();

    var email = $("form[name='change_password'] > input[name='email']").val();
    var newPassword = $("#change_password_new_password").val();
    var repeatNewPassword = $("#change_password_repeat_new_password").val();

    var data = {
        'email': email,
        'new_password': newPassword,
        'repeat_new_password': repeatNewPassword,
        'csrfmiddlewaretoken': csrf_token
    };

    $.ajax({
        type: 'POST',
        url: '/ajax/account/password/update',
        data: data,
        dataType: 'json',
        success: function (response) {
            console.log(response)
            if (response.status) {
                // $('#passwordChangeModal').modal('hide'); 
                // $("form[name='change_password']")[0].reset();  
                window.location = '/accounts/profile/'
            } else {
                $('#change_password_errorbox').text(response.message);
            }
        },
        error: function (xhr, errmsg, err) {
            console.log(errmsg);
        }
    });
});

$("form[name='full_change_password']").submit(function (event) {
    event.preventDefault();

    var email = $("#full_change_password_email").val();

    var data = {
        "email": email,
        'csrfmiddlewaretoken': csrf_token
    };

    $("#full_change_password_but").attr("disabled", "disabled")

    $.ajax({
        type: 'POST',
        url: '/ajax/account/full_password/update',
        data: data,
        dataType: 'json',
        success: function (response) {
            $("#full_change_password_but").removeAttr('disabled');
            if (response.status) {
                $('#full_change_password_successbox').text(response.message);
            } else {
                $('#full_change_password_errorbox').text(response.message);
            }
        },
        error: function (xhr, errmsg, err) {
            console.log(errmsg);
        }
    });
});


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
    var warehouse = $("#buy_warehouse_select option:selected");
    const warehouseId = warehouse.val();
    const warehouseModel = warehouse.data("model")
    if (!id.length > 0) { id = null }
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
            warehouseId: warehouseId,
            warehouseModel: warehouseModel,
            csrfmiddlewaretoken: csrf_token
        },
        method: 'POST',
        url: '/ajax/inbox/create'
    }).then((response) => {
        if (response.status) {
            if (status === "BUYOUT") {
                return window.location.reload()
            }
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
    var first_name = $('#address_form_first_name').val();
    var last_name = $('#address_form_last_name').val();
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
            first_name: first_name,
            last_name: last_name,
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
            // window.location.href = '/accounts/profile/packages/'
            window.location.reload()
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
    var telegram = $('#edit_profile_form_telegram').val();
    var country = $('#country_selector_2').val();

    console.log(first_name, last_name, sur_name, country)

    $("#edit_profie_but").attr('disabled', 'disabled');

    $.ajax({
        data: {
            first_name: first_name,
            last_name: last_name,
            sur_name: sur_name,
            telegram: telegram,
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

function updateIsDeliveried(purchaseId) {
    $.ajax({
        data: {
            purchase: parseInt(purchaseId),
            csrfmiddlewaretoken: csrf_token
        },
        method: 'POST',
        url: '/ajax/accounts/profile/purchases/status/update'
    }).then((response) => {
        if (response.status) {
            window.location.reload()
        } else {
            console.log(response)
        }
    })
}

function payPurchase(purchaseId) {
    $.ajax({
        data: {
            purchase: parseInt(purchaseId),
            csrfmiddlewaretoken: csrf_token
        },
        method: 'POST',
        url: '/ajax/accounts/profile/purchases/pay'
    }).then((response) => {
        if (response.status) {
            console.log(response.pay_url)
            window.location.href = response.pay_url
        } else {
            console.log(response)
        }
    })
}

function detectLanguage() {
    var url = window.location.href;
    var locale = "ru";
    if (url.includes("/ru/")) {
        locale = "ru"
    } else {
        locale = "en"
    }
    return locale;
}

function deleteUserWarehouse(warehouseId) {
    var locale = detectLanguage()
    var messages = {
        "en": "Are you sure you want to delete the warehouse?",
        "ru": "Вы уверены, что хотите удалить склад?",
    }
    var message = messages[locale]
    var confirmation = confirm(message);
    if (confirmation) {
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
            console.log(purchaseId)
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



function removePurchase(idx) {
    var url = window.location.href;
    var locale = "ru";
    if (url.includes("/ru/")) {
        locale = "ru"
    } else {
        locale = "en"
    }
    var messages = {
        "en": "Are you sure you want to delete this purchase?",
        "ru": "Вы уверены, что хотите удалить эту покупку?",
    }
    var message = messages[locale]
    var confirmation = confirm(message);
    if (confirmation) {
        var requestData = {
            idx: parseInt(idx),
            csrfmiddlewaretoken: csrf_token
        };

        $.ajax({
            data: requestData,
            method: 'POST',
            url: '/ajax/accounts/profile/purchases/remove',
        }).then((response) => {
            if (response.status) {
                window.location.reload()
            }
        }).catch((response) => {
            console.log(response)
        });
    }
}

$("#profile-image").on("click", function () {
    $("#profile-image-input").click();
});

$('#profile-image-input').change(function (e) {
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
            success: function (response) {
                $('#profile-image').attr('src', response.image_url);
            },
            error: function (error) {
                console.log(error);
            }
        });
    }
});



function skipAddressForm() {
    window.location.reload()
}

$("input.warehouseSwitch").change(function (e) {
    e.preventDefault();
    var locale = detectLanguage()
    var open_messages = {
        "en": "Are you sure you want to open a warehouse?",
        "ru": "Вы уверены что хотите открыть склад?",
    }
    var close_messages = {
        "en": "Are you sure you want to close a warehouse?",
        "ru": "Вы уверены что хотите закрыть склад?",
    }
    var closed_messages = {
        "en": "Closed",
        "ru": "Закрыт",
    }
    var opened_messages = {
        "en": "Opened",
        "ru": "Открыт",
    }
    var isChecked = $(this).prop("checked");
    var message = open_messages[locale];
    if (!isChecked) {
        message = close_messages[locale];
    }    else {
        message = open_messages[locale];
    }
    var confirmation = confirm(message);
    var warehouseId = $(this).data('warehouse')
    var label = $(this).next();
    if (confirmation) {
        $.ajax({
            data: {
                warehouse: parseInt(warehouseId),
                csrfmiddlewaretoken: csrf_token
            },
            method: 'POST',
            url: '/ajax/accounts/profile/warehouses/update',
        }).then((response) => {
            if (response.status) {
                $(this).prop("checked", response.warehouse_is_opened);
                if (response.warehouse_is_opened) {
                    label.text(opened_messages[locale]);
                } else {
                    label.text(closed_messages[locale]);
                }
            } else {
                console.log(response)
            }
        })
    }
})


function changeRemark(self, purchase) {
    var remark = $(self).data("remark");
    $("#purchaseRemarkInput").val(remark)
    $("#purchaseRemark").data("purchase", purchase)
    $("#purchaseRemarkModal").modal("show");
}


$("#purchaseRemark").submit(function(e) {
    e.preventDefault();

    var purchase = $(this).data("purchase");
    var purchaseRemark = $("#purchaseRemarkInput").val();
    var purchaseRemarks = document.querySelectorAll("td.purchaseRemark")

    var requestData = {
        purchase: parseInt(purchase),
        remark: purchaseRemark,
        csrfmiddlewaretoken: csrf_token
    };

    $.ajax({
        data: requestData,
        method: 'POST',
        url: '/ajax/accounts/profile/purchases/remark/update',
    }).then((response) => {
        if (response.status) {
            $("#purchaseRemarkModal").modal("hide");
            for (var i = 0; purchaseRemarks.length; i++) {
                var spurchase = purchaseRemarks[i]
                if (spurchase.dataset.purchase == purchase) {
                    spurchase.innerHTML = purchaseRemark
                }
            }
        }
    }).catch((response) => {
        console.log(response)
    });
})



function changeTrackAfterSent(self, purchase) {
    var track = $(self).data("track");
    $("#purchaseTrackAfterSentInput").val(track)
    $("#purchaseTrackAfterSent").data("purchase", purchase)
    $("#purchaseTrackAfterSentModal").modal("show");
}


$("#purchaseTrackAfterSent").submit(function(e) {
    e.preventDefault();

    var purchase = $(this).data("purchase");
    var purchaseTrackAfterSents = document.querySelectorAll("td.purchaseTrackAfterSent")
    var last_track_number = $("#purchaseTrackAfterSentInput").val();

    var requestData = {
        purchase: parseInt(purchase),
        track_after_sent: last_track_number,
        csrfmiddlewaretoken: csrf_token
    };

    $.ajax({
        data: requestData,
        method: 'POST',
        url: '/ajax/accounts/profile/purchases/last_track_number/update',
    }).then((response) => {
        if (response.status) {
            $("#purchaseTrackAfterSentModal").modal("hide");
            for (var i = 0; purchaseTrackAfterSents.length; i++) {
                var spurchase = purchaseTrackAfterSents[i]
                if (spurchase.dataset.purchase == purchase) {
                    spurchase.innerHTML = last_track_number
                }
            }
        }
    }).catch((response) => {
        console.log(response)
    });
})