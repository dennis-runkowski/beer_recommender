// Materialize
$(document).ready(function(){
    $('.sidenav').sidenav();
});
// Main Click Events
$(function () {
    checkLogin();
    getSearch('*', '');
    $('#nav_sign_up').click(function (e) {
        $('.section_class').hide()
        $('#section_sign_up').show()
    })
    $('#nav_login').click(function (e) {
        $('.section_class').hide()
        $('#section_login').show()
    })
    $('.nav_header').click(function (e) {
        $('.section_class').hide()
        $('#section_search').show()
    })
    $('#nav_add').click(function (e) {
        $('.section_class').hide()
        $('#section_add').show()

        $.ajax({
            url: '/api/v1/get_styles',
            type: 'GET',
            success: function (response) {
                if (response.status === 'success') {
                    $.each(response.data.styles, function (index, value) {
                        $('#style_add').append('<option value=' + value + '>' + value + '</>')
                    })
                    $('select').formSelect();
                }
            }
        }) 
    })
    $('#section_forgot').click(function (e) {
        $('.section_class').hide()
        $('#section_forgot_password').show()
    })
    // Logout click event
    $('#nav_logout').click(function (e) {
        sessionStorage.removeItem('token');
        M.toast({html: 'You are now logged out!'});
        checkLogin();
    });
    // Select dropdowns
    $(document).ready(function(){
        $('select').formSelect();
      });
})





