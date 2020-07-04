$(document).ready(function()
{
    var rand = Math.random()
    var url = "/reaper/aviation/biplane/buildlog/data.py?r=" +rand.toString();

    $.getJSON(url,
    function(data)
    {
        var tr;
        var total_hrs = 0;
        for (var i=0; i<data.length; i++)
        {
            total_hrs += parseFloat(data[i][2]);
            tr = $('<tr/>');
            tr.append("<td>" + data[i][0] + "</td>"); // date
            tr.append("<td>" + data[i][2] + "</td>"); // hours
            tr.append("<td>" + niceify(data[i][1]) + "</td>"); // activity
            if (data[i][9] == "")
            {
                tr.append("<td> No picture </td>");
            }
            else
            {
                var smallname = get_smallname(data[i][9]);
                var img = "<img src=\"" + smallname + "\">";
                tr.append("<td><a href=\"" + data[i][9] + "\">" + img +
                    "</a></td>");
            }
            $('.logtable').append(tr);
        }
        tr = $('<tr/>');
        tr.append("<td><b>Total</b></td>");
        tr.append("<td>" + total_hrs.toFixed(1) + "</td>"); // hours
        tr.append("<td/>");
        tr.append("<td/>");
        $('.logtable').append(tr);
    });
});

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