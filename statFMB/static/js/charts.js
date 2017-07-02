function showError(errorType){
  //if (errorType === undefined) { break; }
  clearError();

  var errorMsg = document.getElementById("error-message");

  document.getElementById("error-div").style.display = "block";

  if (errorType === "noChart") {
    errorMsg.innerText = "nenhum tipo de gráfico selecionado!";
  } else {
    errorMsg.innerText = "tipo de erro desconhecido!";
  }
}

function clearError(){
  document.getElementById("error-div").style.display = "none";
  document.getElementById("error-message").innerText = "";
}

function clearChart(){
  document.getElementById("chart-container").innerHTML = "";
}

function generateMap(){
  var chartContainer = document.getElementById("chart-container");

  if (document.getElementById("maps-world").checked){
    return generateTest();
  } else if (document.getElementById("maps-europe").checked){
    return Date();
  } else if (document.getElementById("maps-portugal").checked){
    return Date();
  } else {
    showError("noChart");
  }
}

function generatePie(){
  var chartContainer = document.getElementById("chart-container");

  if (document.getElementById("pie-gates").checked){
    return generatePieGates();
  } else if (document.getElementById("pie-countries").checked){
    return Date();
  } else if (document.getElementById("pie-municipalities").checked){
    return Date();
  } else {
    showError("noChart");
  }
}

function generatePieGates(){
      // Build the chart
    var chart = Highcharts.chart('chart-container', {
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'pie'
        },
        title: {
            text: 'Browser market shares January, 2015 to May, 2015'
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: false
                },
                showInLegend: true
            }
        },
        series: [{
            name: 'Brands',
            colorByPoint: true,
            data: [{
                name: 'Microsoft Internet Explorer',
                y: 56.33
            }, {
                name: 'Chrome',
                y: 24.03,
                sliced: true,
                selected: true
            }, {
                name: 'Firefox',
                y: 10.38
            }, {
                name: 'Safari',
                y: 4.77
            }, {
                name: 'Opera',
                y: 0.91
            }, {
                name: 'Proprietary or Undetectable',
                y: 0.2
            }]
        }]
    });
  return chart;
}

function generateTest(){
var chart =Highcharts.chart('chart-container', {

    title: {
        text: 'Tipos de Veículos'
    },

    subtitle: {
        text: 'Periodo: aaa'
    },

    yAxis: {
        title: {
            text: 'Numero de entradas'
        }
    },

    xAxis: {
        //TODO: place period.designation here
        categories: ['aa','bb']
    },

    legend: {
        layout: 'vertical',
        align: 'right',
        verticalAlign: 'middle'
    },

    plotOptions: {
        series: {
            pointStart: 0
        }
    },

    series: [{
        name: 'Moto',
        data: []
    }, {
        name: 'Ligeiro',
        data: [24916, 24064, 29742, 29851, 32490, 30282, 38121, 40434]
    }, {
        name: 'Ligeiro XL',
        data: [11744, 17722, 16005, 19771, 20185, 24377, 32147, 39387]
    }, {
        name: 'Caravana',
        data: [null, null, 7988, 12169, 15112, 22452, 34400, 34227]
    }, {
        name: 'Autocarro',
        data: [12908, 5948, 8105, 11248, 8989, 11816, 18274, 18111]
    }]
});
  return chart;
}
