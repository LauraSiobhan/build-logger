$(document).ready(function()
{
	var url = "file:///home/reaper/devel/build-logger/data.json";

	$.getJSON(url,
	function(data)
	{
		var tr;
		for (var i=0; i<data.length; i++)
		{
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
				tr.append("<td><a href=\"" + data[i][9] + "\">Picture</a></td>");
			}
			$('table').append(tr);
		}
	});
});

function niceify(text)
{
	// make the text more nicer: honor \n chars, etc.
	return text.replace(/\n/g, "<br>");
}
