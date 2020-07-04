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
        var total_hours = 0;

        var monthly_progress = [
            {
                curr_month: "",
                curr_index: 0,
                x: [],
                y: [],
                type: "bar"
            }
        ];

        var category_hours = [
            {
                categories: {},
                x: [],
                y: [],
                type: "bar",
                orientation: "h"
            }
        ];

        var monthly_rate = {
            total_hours: 0,
            first_day: "",
            hours: 0,
            month_ago_timestamp: Date.now() - (30 * 24 * 3600 * 1000)
        };

        var thirty_day = [
            {
                dates: {},
                total_hours: 0,
                month_ago_timestamp: Date.now() - (30 * 24 * 3600 * 1000),
                x: [],
                y: [],
                type: "bar"
            }
        ];

        // we assume entries are in date order
        for (var i=0; i<data.length; i++)
        {
            calc_monthly_progress(data[i], monthly_progress);
            calc_category_hours(data[i], category_hours);
            calc_monthly_rate(data[i], monthly_rate);
            calc_thirty_day(data[i], thirty_day);
            total_hours += parseFloat(data[i][2]);
        }

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
    var this_date = raw_data[0];
    [year, month, day] = this_date.split(' ')[0].split('-');
    var this_month = year + "-" + month;
    if (this_month != plot_data[0].curr_month)
    {
        plot_data[0].curr_index++;
        plot_data[0].x[plot_data[0].curr_index] = this_month;
        plot_data[0].y[plot_data[0].curr_index] = 0;
        plot_data[0].curr_month = this_month;
    }
    var hours = raw_data[2];
    plot_data[0].y[plot_data[0].curr_index] += parseFloat(hours);
}


function calc_category_hours(raw_data, plot_data)
{
    var cat = raw_data[5];
    var hours = parseFloat(raw_data[2]);
    if (cat in plot_data[0].categories)
    {
        plot_data[0].categories[cat] += hours;
    }
    else
    {
        plot_data[0].categories[cat] = hours;
    }
}


function calc_monthly_rate(raw_data, plot_data)
{
    var this_date = raw_data[0];
    var this_timestamp = new Date(this_date).getTime();
    var hours = parseFloat(raw_data[2]);

    plot_data.total_hours += hours;
    if (plot_data.first_day == "")
    {
        plot_data.first_day = this_date;
    }

    if (this_timestamp > plot_data.month_ago_timestamp)
    {
        plot_data.hours += hours;
    }
}

function calc_thirty_day(raw_data, plot_data)
{
    var this_date = raw_data[0];
    var date_only = this_date.split(' ')[0];
    var this_timestamp = new Date(this_date).getTime();
    var hours = parseFloat(raw_data[2]);

    if (this_timestamp > plot_data[0].month_ago_timestamp)
    {
        plot_data[0].total_hours += hours;
        if (plot_data[0].dates[date_only])
        {
            plot_data[0].dates[date_only] += hours;
        }
        else
        {
            plot_data[0].dates[date_only] = hours;
        }
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
    //layout.title = "Hours Spent by Category";
    //layout.xaxis.title = "Hours";
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
    plot_data[0].x = Object.values(plot_data[0].categories);
    plot_data[0].y = Object.keys(plot_data[0].categories);
    Plotly.newPlot("category_hours", plot_data, layout);
}


function plot_monthly_rate(layout, plot_data)
{
    var first_millis = new Date(plot_data.first_day).getTime();
    var proj_len_millis = new Date().getTime() - first_millis;
    var proj_len_days = proj_len_millis / (24 * 60 * 60 * 1000);
    var overall_avg = plot_data.total_hours / proj_len_days;
    var upper_limit = Math.floor(overall_avg * 15);
    var rate = plot_data.hours / 30;
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
