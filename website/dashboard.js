$(document).ready(function()
{
    var rand = Math.random()
    var url = "/reaper/aviation/biplane/buildlog/statdata.py?r=" +rand.toString();
    var month_names = [];
    var month_hours = [];

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

        var monthly_progress = [
            {
                x: [],
                y: [],
                type: "bar"
            }
        ];

        var category_hours = [
            {
                x: [],
                y: [],
                type: "bar",
                orientation: "h"
            }
        ];

        var monthly_rate = {};

        var thirty_day = [
            {
                x: [],
                y: [],
                type: "bar"
            }
        ];

        calc_monthly_progress(data, monthly_progress);
        calc_category_hours(data, category_hours);
        calc_monthly_rate(data, monthly_rate);
        calc_thirty_day(data, thirty_day);

        plot_monthly_progress(base_layout, monthly_progress);
        plot_overall_progress(base_layout, total_hours);
        plot_category_hours(base_layout, category_hours);
        plot_monthly_rate(base_layout, monthly_rate);
        plot_thirty_day(base_layout, thirty_day);
    });
});


/* ----------------------------------------------------------------------
 * calc functions
 * ----------------------------------------------------------------------*/

function calc_monthly_progress(raw_data, plot_data)
{
    var monthly_data = raw_data.hours_by_month;
    for (date in monthly_data)
    {
        plot_data[0].x.push(date);
        plot_data[0].y.push(monthly_data[date])
    }
}


function calc_category_hours(raw_data, plot_data)
{
    var cat_hours = raw_data.hours_by_category;
    for (cat in cat_hours)
    {
        plot_data[0].y.push(cat);
        plot_data[0].x.push(cat_hours[cat]);
    }
}


function calc_monthly_rate(raw_data, plot_data)
{
    plot_data.overall_avg = raw_data.avg_overall;
    plot_data.month_avg = raw_data.avg_last_month;
}

function calc_thirty_day(raw_data, plot_data)
{
    var thirty_day = raw_data.hours_last_30;
    for (date in thirty_day)
    {
        plot_data[0].x.push(date);
        plot_data[0].y.push(thirty_day[date]);
    }
}

/* ----------------------------------------------------------------------
 * plot functions
 * ----------------------------------------------------------------------*/

function plot_monthly_progress(layout, plot_data)
{
    layout.title = "Hours Spent by Month";
    layout.yaxis.title = "Hours";
    Plotly.newPlot("monthly_progress", plot_data, layout);
}


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


function plot_category_hours(herplayout, plot_data)
{
    var layout = 
    {
        title: "Hours Spent by Category",
        paper_bgcolor: "#000",
        plot_bgcolor: "#000",
        font: { color: "#fff" },
        xaxis: {
            title: "Hours",
            gridcolor: "#444",
            tickcolor: "#555"
        },
        yaxis: {
            gridcolor: "#444",
            tickcolor: "#555"
        }
    };
    Plotly.newPlot("category_hours", plot_data, layout);
}


function plot_monthly_rate(layout, plot_data)
{
    var overall_avg = plot_data.overall_avg;
    var rate = plot_data.month_avg;
    var upper_limit = 4;
    layout.title = "Avg hours per day, last 30 days";
    var monthly_rate = [
          {
            domain: { x: [0, 1], y: [0, 1] },
            value: rate,
            title: { text: "Hours/day vs. overall avg", font: { size: 12 } },
            type: "indicator",
            mode: "gauge+number+delta",
            delta: { reference: overall_avg },
            gauge: { 
                axis: { range: [null, upper_limit] },
                steps: [
                    { range: [0, overall_avg], color: "#333" },
                    { range: [overall_avg, upper_limit], color: "black" }
                ]
            }
          }
    ];
    Plotly.newPlot("monthly_rate", monthly_rate, layout);
}

function plot_thirty_day(layout, plot_data)
{
    var avg_hours = plot_data[0].total_hours / 30;
    for (date in plot_data[0].dates)
    {
        plot_data[0].x.push(date);
        plot_data[0].y.push(plot_data[0].dates[date]);
    }

    layout.title = "Daily hours, last 30 days";
    layout.yaxis.title = "Hours";
    layout.shapes = [{
        type: 'line',
        xref: 'paper',
        x0: 0,
        y0: avg_hours,
        x1: 1,
        y1: avg_hours,
        line: {
            color: 'green',
            width: 2,
            dash: 'dot'
        }
    }];
    Plotly.newPlot("30_day_chart", plot_data, layout);
}
