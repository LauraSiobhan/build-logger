$(document).ready(function()
{
    $('#pagenum').val("1");
    var pagesize = Number($('#pagesize').val());
    $.ajax(
    {
        url: 'data.py',
        cache: false,
        data: {pagenum: 0, pagesize: pagesize},
        success: add_rows
    });

    // so this is effectively, "on scroll, do this"
    $(window).scroll(
    function()
    {
        var position = $(window).scrollTop();
        var bottom = $(document).height() - $(window).height();

        if (position >= (bottom - 200))
        {
            var pagenum = Number($('#pagenum').val());
            var pagesize = Number($('#pagesize').val());

            $.ajax(
            {
                url: 'data.py',
                cache: false,
                data: {pagenum: pagenum, pagesize: pagesize},
                success: add_rows
            });

            $("#pagenum").val(pagenum + 1);
        }
    });
});

var total_hours;

function add_rows(data)
{
    var tr;
    var events = data.events;
    if (!total_hours) { total_hours = data.total_hours; }
    for (var i=0; i<events.length; i++)
    {
        var hours = events[i][2];
        var hour_word = "hours";
        if (events[i][2] == 1) { hour_word = "hour"; }
        var act = "<td><p><b> " + events[i][0] + " :: " + hours + " " +
                  hour_word + " :: " + Number.parseFloat(total_hours).toFixed(1)
                  + " total </b></p><p> " + niceify(events[i][1]) + " </td>";
        total_hours -= hours;
        tr = $('<tr/>');
        tr.append(act);
        if (events[i][9] == "")
        {
            tr.append("<td> No picture </td>");
        }
        else
        {
            var smallname = get_smallname(events[i][9]);
            var img = "<img src=\"" + smallname + "\">";
            tr.append("<td><a href=\"" + events[i][9] + "\">" + img +
                "</a></td>");
        }
        $('.logtable').append(tr);
    }
}

function niceify(text)
{
    // make the text more nicer: honor \n chars, etc.
    return text.replace(/\n/g, "<br>");
}

function get_smallname(url)
{
    // if the input is foo/bar/baz/quux.jpg, the output is
    // foo/bar/baz/quux-sm.jpg
    var pathbits = url.split('/');
    var filename = pathbits.pop();
    var filebits = filename.split('.');
    for (var i=0; i<filebits.length; i++)
    {
        if (i == filebits.length - 2)
        {
            filebits[i] += '-sm';
        }
        if (i == filebits.length - 1 && filebits[i] == 'JPG')
        {
            filebits[i] = 'jpg';
        }
    }
    var smallfile = pathbits.join('/') + '/' + filebits.join('.');
    return smallfile;
}

