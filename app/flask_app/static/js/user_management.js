// Login Button
$(function () {
    $('#login_button').click(function (e) {
        e.preventDefault();
        $('.errors').html('');
        var data = $('#login_form').serialize();
        $.ajax({
            url: '/users/v1/login',
            data: data,
            type: 'POST',
            success: function (response) {
                if (response.status === 'error') {
                    $.each(response.message, function (index, value) {
                        $(index).html(value)
                    })
                } else if (response.status === 'success') {
                    $('#login_form').trigger('reset');
                    sessionStorage.setItem('token', response.message);
                    M.toast({html: 'Login Successful!'});
                    $("HTML, BODY").animate({ scrollTop: 0 }, 1000);
                    checkLogin();
                }
            }
        })
    });
    $('#forgot_button').click(function (e) {
        e.preventDefault();
        $('.errors').html('');
        var data = $('#forgot_password_form').serialize();
        $.ajax({
            url: '/users/v1/forgot_password',
            data: data,
            type: 'POST',
            success: function (response) {
                if (response.status === 'error') {
                    $.each(response.message, function (index, value) {
                        $(index).html(value)
                    })
                } else if (response.status === 'success') {
                    $('#forgot_password_form').trigger('reset');
                    M.toast({html: 'Check your email for the reset token!'});
                    $('.content_section').hide();
                    $('#content_reset_section').show();
                }
            }
        });
    });
    $('#reset_button').click(function (e) {
        e.preventDefault();
        $('.errors').html('');
        var data = $('#reset_password_form').serialize();
        $.ajax({
            url: '/users/v1/reset_password',
            data: data,
            type: 'POST',
            success: function (response) {
                if (response.status === 'error') {
                    $.each(response.message, function (index, value) {
                        $(index).html(value)
                    })
                } else if (response.status === 'success') {
                    $('#reset_password_form').trigger('reset');
                    M.toast({html: 'Reset Password!'});
                    $('.content_section').hide();
                    $('#content_login_section').show();
                }
            }
        });
    });
});
// Check if a users session is active and logged in
function checkLogin () {
    $.ajax({
        url: '/users/v1/login_check',
        type: 'GET',
        beforeSend: function (xhr) {
            var token = sessionStorage.getItem('token');
            xhr.setRequestHeader('Authorization', 'Bearer: ' + token);
        },
        success: function (response) {
            if (response.status === 'error') {
                $('#nav_login').show();
                $('#nav_logout').hide();
                $('#nav_add').hide();
                $('#login_form').show();
                $('#logged_in').html('');
                sessionStorage.setItem('token', 'loggedOut');
            } else if (response.status === 'success') {
                var login = $('#logged_in');
                login.show();
                login.html('Welcome ' + response.message + '!');
                $('#nav_sign_up').hide();
                $('#nav_login').hide();
                $('#login_form').hide();
                $('#nav_logout').show();
                $('#nav_add').show();
            }
        }
    });
}
// Sign Up
$(function () {
    $('#signup_button').click(function (e) {
        e.preventDefault();
        $('.errors').html('');
        var data = $('#signup_form').serialize();
        $.ajax({
            url: '/users/v1/signup',
            data: data,
            type: 'POST',
            success: function (response) {
                if (response.status === 'error') {
                    $.each(response.message, function (index, value) {
                        $(index).html(value)
                    })
                } else if (response.status === 'success') {
                    $('#signup_form').trigger('reset');
                    M.toast({html: 'Created Your Account!'})
                }
            }
        })
    })
});