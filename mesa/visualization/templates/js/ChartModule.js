const ChartModule = function (series, canvas_width, canvas_height) {
  const canvas = document.createElement("canvas");
  Object.assign(canvas, {
    width: canvas_width,
    height: canvas_height,
    style: "border:1px dotted",
  });
  // Append it to #elements
  const elements = document.getElementById("elements");
  elements.appendChild(canvas);
  // Create the context and the drawing controller:
  const context = canvas.getContext("2d");

  const convertColorOpacity = (hex) => {
    if (hex.indexOf("#") != 0) {
      return "rgba(0,0,0,0.1)";
    }

    hex = hex.replace("#", "");
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);
    return `rgba(${r},${g},${b},0.1)`;
  };

  // Prep the chart properties and series:
  const datasets = [];
  for (const i in series) {
    const s = series[i];
    const new_series = {
      label: s.Label,
      borderColor: s.Color,
      backgroundColor: convertColorOpacity(s.Color),
      data: [],
    };
    datasets.push(new_series);
  }

  const chartData = {
    labels: [],
    datasets: datasets,
  };

  const chartOptions = {
    responsive: true,
    tooltips: {
      mode: "index",
      intersect: false,
    },
    hover: {
      mode: "nearest",
      intersect: true,
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
        },
        ticks: {
          maxTicksLimit: 11,
        },
      },
      y: {
        display: true,
        title: {
          display: true,
        },
      },
    },
  };

  const chart = new Chart(context, {
    type: "line",
    data: chartData,
    options: chartOptions,
  });

  this.render = (data) => {
    chart.data.labels.push(control.tick);
    for (let i = 0; i < data.length; i++) {
      chart.data.datasets[i].data.push(data[i]);
    }
    chart.update();
  };

  this.reset = () => {
    while (chart.data.labels.length) {
      chart.data.labels.pop();
    }
    chart.data.datasets.forEach((dataset) => {
      while (dataset.data.length) {
        dataset.data.pop();
      }
    });
    chart.update();
  };
};
