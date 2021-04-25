$(document).ready(function()
{
    var rand = Math.random()
    var url = "statdata.py?r=" +rand.toString();
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

var subcat_hours = {};
var subcat_mode = 'category';
var cat_data = { x: [], y: [] };
var cat_title = "Hours Spent by Category (click to drill down)";

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

    var subcat_raw = raw_data.hours_by_subcategory;
    for (cat in subcat_raw)
    {
        subcat_hours[cat] = { 
            x: [], 
            y: [], 
            type: 'bar', 
            orientation: 'horizontal'
        };
        for (subcat in subcat_raw[cat])
        {
            subcat_hours[cat].y.push(subcat);
            subcat_hours[cat].x.push(subcat_raw[cat][subcat]);
        }
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
    plot_data[0].total_hours = 0;
    for (date in thirty_day)
    {
        var hours = thirty_day[date];
        plot_data[0].x.push(date);
        plot_data[0].y.push(hours);
        plot_data[0].total_hours += hours;
    }
}

/* ----------------------------------------------------------------------
 * plot functions
 * ----------------------------------------------------------------------*/

function plot_monthly_progress(layout, plot_data)
{
    var local_layout = JSON.parse(JSON.stringify(layout));
    local_layout.title = "Hours Spent by Month";
    local_layout.yaxis.title = "Hours";
    Plotly.newPlot("monthly_progress", plot_data, local_layout);
}


function plot_overall_progress(layout, total_hours)
{
    var local_layout = JSON.parse(JSON.stringify(layout));
    local_layout.title = "Overall progress";
    var total_progress = [
          {
            domain: { x: [0, 1], y: [0, 1] },
            value: total_hours,
            number: { valueformat: '.1f' },
            title: { text: "Hours", font: { size: 12 } },
            type: "indicator",
            mode: "number+gauge",
            gauge: { axis: { range: [null, 6000] } } 
          }
    ];
    Plotly.newPlot("total_progress", total_progress, local_layout);
}


function plot_category_hours(layout, plot_data, subcat_data)
{
    var local_layout = JSON.parse(JSON.stringify(layout));
    local_layout.title = cat_title;
    Plotly.newPlot("category_hours", plot_data, local_layout);
    var myplot = document.getElementById('category_hours');
    myplot.on('plotly_click', expand_cat);
}


function expand_cat(data)
{
    var cat = data.points[0].y;
    var myplot = document.getElementById('category_hours');
    if (subcat_mode == 'category')
    {
        for (item in data.points[0].data.x)
        {
            cat_data.x.push(data.points[0].data.x[item]);
        }
        for (item in data.points[0].data.y)
        {
            cat_data.y.push(data.points[0].data.y[item]);
        }
        subcat_mode = 'subcategory';
        data.points[0].data.x = subcat_hours[cat].x;
        data.points[0].data.y = subcat_hours[cat].y;
        myplot.layout.title.text = "Hours Spent on " + cat +
            " (click to return)";
    }
    else
    {
        data.points[0].data.x = cat_data.x;
        data.points[0].data.y = cat_data.y;
        myplot.layout.title.text = cat_title;
        subcat_mode = 'category';
    }
    Plotly.redraw("category_hours");
}


function plot_monthly_rate(layout, plot_data)
{
    var overall_avg = plot_data.overall_avg;
    var rate = plot_data.month_avg;
    var upper_limit = 4;
    var local_layout = JSON.parse(JSON.stringify(layout));
    local_layout.title = "Avg hours per day, last 30 days";
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
    Plotly.newPlot("monthly_rate", monthly_rate, local_layout);
}

function plot_thirty_day(layout, plot_data)
{
    var avg_hours = plot_data[0].total_hours / 30;
    for (date in plot_data[0].dates)
    {
        plot_data[0].x.push(date);
        plot_data[0].y.push(plot_data[0].dates[date]);
    }

    var local_layout = JSON.parse(JSON.stringify(layout));
    local_layout.title = "Daily hours, last 30 days";
    local_layout.yaxis.title = "Hours";
    local_layout.shapes = [{
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
    Plotly.newPlot("30_day_chart", plot_data, local_layout);
}
