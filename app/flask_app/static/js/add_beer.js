// add beer to the database

$(function () {
    console.log('add')
    $('#add_beer_button').click(function (e) {
        console.log('button click')
        e.preventDefault();
        $('.errors').html('');
        var data = $('#add_form').serialize();
        $.ajax({
            url: '/api/v1/add_beer',
            data: data,
            type: 'POST',
            success: function (response) {
                if (response.status === 'error') {
                    console.log(response)
                    $.each(response.message, function(key, value) {
                        $(key).html(value)
                    })
                } else if (response.status === 'success') {
                    $('#add_form').trigger('reset');
                    M.toast({html: 'Added beer!'});
                    
                }
            }
        })
    });
})