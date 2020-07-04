$(document).ready(function()
{
    var rand = Math.random()
    var url = "/reaper/aviation/biplane/buildlog/statdata.py?r=" +rand.toString();
    var base_layout = 
    {
        paper_bgcolor: "#000",
        plot_bgcolor: "#000",
        font: { color: "#fff" },
        xaxis: {
            gridcolor: "#444",
            tickcolor: "#555"
        },
        yaxis: {
            gridcolor: "#444",
            tickcolor: "#555"
        }
    };

    $.getJSON(url,
    function(data)
    {
        var total_hours = data.total_hours;

        plot_overall_progress(base_layout, total_hours);
    });
});


function plot_overall_progress(layout, total_hours)
{
    layout.title = "Overall progress";
    var total_progress = [
          {
            domain: { x: [0, 1], y: [0, 1] },
            value: total_hours,
            number: { valueformat: '.1f' },
            title: { text: "Hours", font: { size: 12 } },
            type: "indicator",
            mode: "number+gauge",
            gauge: { axis: { range: [null, 4000] } } 
          }
    ];
    Plotly.newPlot("total_progress", total_progress, layout);
}
