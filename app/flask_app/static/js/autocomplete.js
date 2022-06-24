
$('#search_bar').keyup(function(e) {
    if (e.keyCode != 13) {
        var prefix = $('#search_bar').val();
        // const instance = M.Autocomplete.getInstance(document.getElementById('search_bar'));
        if (prefix && prefix !== '/') {
            $.ajax({
                url: '/api/v1/autocomplete/' + encodeURIComponent(prefix),
                contentType: 'application/json',
                type: 'GET',
                success: function (response) {
                    // instance.options.data = response.data;
                    autoComplete(document.getElementById("search_bar"), response.data, prefix)

                }
            })
        } else {
            $('#search_barautocomplete-list').remove()
        }
    }
})
function autoComplete(inp, arr, prefix) {
    /*the autocomplete function takes two arguments,
    the text field element and an array of possible autocompleted values:*/
    var a, b, i, val = prefix;
    closeAllLists();
    a = document.createElement("DIV");
    if (arr.titles.length > 0) {
        title = document.createElement("DIV")
        title.setAttribute("class", "autocomplete-header")
        title.innerHTML = "Beer Names"
        a.setAttribute("id", inp.id + "autocomplete-list");
        a.setAttribute("class", "z-depth-4 autocomplete-items");
        inp.parentNode.appendChild(a);
        a.appendChild(title)
        $.each(arr.titles, function(index, value) {
            b = document.createElement("DIV");
            b.innerHTML = "<strong>" + value.substr(0, val.length) + "</strong>";
            b.innerHTML += value.substr(val.length);
            b.innerHTML += "<input type='hidden' value='" + value + "'>";
            b.addEventListener("click", function(e) {
                inp.value = this.getElementsByTagName("input")[0].value;
                closeAllLists();
                var sortBy = $('.active_class').attr('data-sort');
                getSearch(this.getElementsByTagName("input")[0].value, sortBy)
            });
            a.appendChild(b);
        });
    };
    if (arr.styles.length > 0) {
        style = document.createElement("DIV")
        style.setAttribute("class", "autocomplete-header")
        style.setAttribute("id", "style-header")
        style.innerHTML = "Beer Styles"
        a.appendChild(style)
        $.each(arr.styles, function(index, value) {
            b = document.createElement("DIV");
            b.innerHTML = "<strong>" + value.substr(0, val.length) + "</strong>";
            b.innerHTML += value.substr(val.length);
            b.innerHTML += "<input type='hidden' value='" + value + "'>";
            b.addEventListener("click", function(e) {
                inp.value = this.getElementsByTagName("input")[0].value;
                closeAllLists();
                var sortBy = $('.active_class').attr('data-sort');
                getSearch(this.getElementsByTagName("input")[0].value, sortBy)
            });
            a.appendChild(b);
        });
    };
    if (arr.brewer.length > 0) {
        brewer = document.createElement("DIV")
        brewer.setAttribute("class", "autocomplete-header")
        brewer.setAttribute("id", "brewer-header")
        brewer.innerHTML = "Brewer"
        a.appendChild(brewer)
        $.each(arr.brewer, function(index, value) {
            b = document.createElement("DIV");
            b.innerHTML = "<strong>" + value.substr(0, val.length) + "</strong>";
            b.innerHTML += value.substr(val.length);
            b.innerHTML += "<input type='hidden' value='" + value + "'>";
            b.addEventListener("click", function(e) {
                inp.value = this.getElementsByTagName("input")[0].value;
                closeAllLists();
                var sortBy = $('.active_class').attr('data-sort');
                getSearch(this.getElementsByTagName("input")[0].value, sortBy)
            });
            a.appendChild(b);
        });
    };


    /*execute a function when someone clicks in the document:*/
    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
    });
    inp.addEventListener("keydown", function(e) {
        if (e.keyCode == 13) {
            $('.autocomplete-header').click()
            $('#search_barautocomplete-list').remove()
            
        }
    })
    function closeAllLists(elmnt) {
        /*close all autocomplete lists in the document,
        except the one passed as an argument:*/
        // var inp = document.getElementById("search_bar")
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }
}