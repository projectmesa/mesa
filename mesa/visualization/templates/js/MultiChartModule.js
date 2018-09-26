var MultiChartModule = function(parameter, simulations) {
    var simulations = simulations
    // Create the tag:
    var canvas = document.createElement("canvas");
    document.getElementById("elements").append(canvas)

    var context = canvas.getContext("2d");

    // Prep the chart properties and series:
    var datasets = []
    for (let i=0; i<simulations;i++) {
        var new_series = {
            label: "simulation " + i,
            borderColor: "black",
            data: [],
        };
        datasets.push(new_series);
    }

    var chartData = {
        labels: [],
        datasets: datasets,
    };

    var chartOptions = {
        responsive: true,
        tooltips: {
            mode: 'index',
            intersect: false
        },
        hover: {
            mode: 'nearest',
            intersect: true
        },
        scales: {
            xAxes: [{
                display: true,
                scaleLabel: {
                    display: true
                },
                ticks: {
                    maxTicksLimit: 11
                }
            }],
            yAxes: [{
                display: true,
                scaleLabel: {
                    display: true
                }
            }]
        }
    };

    var chart = new Chart(context, {
        type: 'line',
        data: chartData,
        options: chartOptions
    });

    this.render = function(data, simulation) {
        if (chart.data.labels[chart.data.labels.length -1] != control.tick) {
            chart.data.labels.push(control.tick);
        };
        chart.data.datasets[simulation].data.push(data);
        chart.update();
    };

    this.reset = function() {
        chart.data.labels = []
        console.log(chart.data)
        // while (chart.data.labels.length) { chart.data.labels.pop(); }
        for (dataset of chart.data.datasets) {
            dataset.data = []
        };
        chart.update();
    };
};
