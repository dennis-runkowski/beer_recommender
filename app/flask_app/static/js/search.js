$('#search_bar').keypress(function(event){
    var keycode = (event.keyCode ? event.keyCode : event.which);
    if (keycode == '13'){
        var searchQuery = $('#search_bar').val();
        $('#search_results').html('');
        var sortBy = $('.active_class').attr('data-sort');
        if (searchQuery) {
            getSearch(searchQuery, sortBy)
        } else {
            getSearch("*", sortBy)
        };
    }
});
$('.sort_click').click(function (e) {
    var elementId = '#' + e.currentTarget.getAttribute('id');
    var sortBy = e.currentTarget.getAttribute('data-sort');
    if ($(elementId).hasClass('active_class')) {
        $('.sort_click').removeClass('active_class');
        sortBy = '';
    } else {
        $('.sort_click').removeClass('active_class');
        $(elementId).addClass('active_class');
    }
    var searchQuery = $('#search_bar').val();
    if (!searchQuery) {
        searchQuery = '*';
    }
    getSearch(searchQuery, sortBy)
})
function getSearch(query, sort) {
    var data = {
        'search_query': query,
        'sort_by': sort
    };
    $.ajax({
        url: '/api/v1/search',
        contentType: 'application/json',
        data: JSON.stringify(data),
        type: 'POST',
        success: function (response) {
            if (response.status === 'error') {
                $.each(response.message, function (index, value) {
                    M.toast({html: value});
                    $(index).html(value)
                })
            } else if (response.status === 'success') {
                searchResults(response)
                
            }
        }
    })
}
function searchResults(response) {
    // Destroy click events
    $('.thumbs').off('click');
    $('#search_results').html('');
    $('.errors').html('');
    $('#total_beers').html(response.total + ' Cold Ones')
    if (!response.total) {
        $('#search_results').append('<h4 class="center"> No beers found, please try a different query :) </h4>');
    }
    $.each(response.data, function(index, value) {
        if (value.abv == '0.0') {
            value.abv = 'N/A'
        }
        if (value.ibu == '0.0') {
            value.ibu = 'N/A'
        }
        var thumbDownClass = 'material-icons';
        if (value.user_thumbs_down) {
            thumbDownClass = thumbDownClass + ' active_thumb';
        }
        var thumbUpClass = 'material-icons';
        if (value.user_thumbs_up) {
            thumbUpClass = thumbUpClass + ' active_thumb';
        }
        card = '<div class="card horizontal">' +
                    '<div class="card-stacked">' +
                        '<div class="card-content" data-beer=' + value.id +'>' +
                            '<div class="card_title">' + value.title + '<span class="right thumbs" data-thumb="up"><i class="' + thumbUpClass + '">thumb_up</i></span><span class="right thumbs" data-thumb="down"><i class="' + thumbDownClass + '">thumb_down</i></span></div>' +
                            '<div class="card_meta">' + value.description + '</div>' +
                            '<div class="card_chips"><div class="chip">' + value.style + '</div><div class="chip">ABV:' + value.abv + '</div><div class="chip">IBU:' + value.ibu + '</div></div>' +
                        '</div>' +
                        '<div class="card-action">' +
                            '<a href="' + value.brewer_url + '" target="_blank">' + value.brewer + '</a>'
        if (value.brewer_facebook) {
            card = card + '<span><a href="' + value.brewer_facebook + '" target="_blank"><img src="/static/img/facebook_icon.png"></a> </span>'
        }
        if (value.brewer_instagram) {
            card = card + '<span><a href="' + value.brewer_instagram + '" target="_blank"><img src="/static/img/instagram.png"></a> </span>'
        }
        if (value.brewer_twitter) {
            card = card + ' <span><a href="' + value.brewer_twitter + '" target="_blank"><img src="/static/img/twitter.png"></a> </span>'
        }
        card = card  + '<div class="card_meta">' + value.brewer_description + '</div></div></div></div>'
        $('#search_results').append(card);
    })
    $('.thumbs').click(function (e) {
        var card = $(this).parents('.card-content').first();
        var data = {
            'action': e.currentTarget.getAttribute('data-thumb'),
            'beer_id': card[0].getAttribute('data-beer')
        }
        console.log(data)
        var that = this
        $.ajax({
            url: '/api/v1/beer_action',
            contentType: 'application/json',
            data: JSON.stringify(data),
            type: 'POST',
            success: function (response) {
                if (response.status === 'error') {
                    $.each(response.message, function (index, value) {
                        M.toast({html: value});
                        $(index).html(value)
                    })
                } else if (response.status === 'success') {
                    if (response.message === 'added') {
                        $(that).addClass('active_thumb')
                    } else if (response.message === 'removed') {
                        $(that).removeClass('active_thumb')
                    }
                    
                }
            }
        })
    
    });
}