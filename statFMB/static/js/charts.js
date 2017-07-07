function showError(errorType){
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
  $("#error-div").css("display","none");
  $("error-message").empty();
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
  return showError();
}

//TODO: fine tune graphs with options!!
function generatePie(search){
  var chartContainer = document.getElementById("chart-container");

  if (document.getElementById("pie-gates").checked){
    title = "Top Portas";
    subtitle = "Entradas por porta";

    var data_gates = [];
    for (var key_gate in search.tops.gates){
      if (search.tops.gates.hasOwnProperty(key_gate)) {
        gate_data = [key_gate, search.tops.gates[key_gate]];
        data_gates.push(gate_data);
      }
    }
    return generatePieChart(data_gates,title,subtitle);

  } else if (document.getElementById("pie-countries").checked){
    title = "Top Concelhos";
    subtitle = "Entradas por concelho (+100 entradas)";

    var data_countries = [];
    for (var key_country in search.tops.countries){
      if (search.tops.countries.hasOwnProperty(key_country)) {
        if (search.tops.countries[key_country] >= 100){
          country_data = [key_country,search.tops.countries[key_country]];
          data_countries.push(country_data);
        }
      }
    }
    return generatePieChart(data_countries,title,subtitle);

  } else if (document.getElementById("pie-municipalities").checked){
    title = "Top Paises";
    subtitle = "Entradas por pais (+100 entradas)";

    var data_municipalities = [];
    for (var key_municipality in search.tops.municipalities){
      if (search.tops.municipalities.hasOwnProperty(key_municipality)) {
        if (search.tops.municipalities[key_municipality] >= 100){
          municipality_data = [key_municipality,
                          search.tops.municipalities[key_municipality]];
          data_municipalities.push(municipality_data);
        }
      }
    }
    return generatePieChart(data_municipalities,title,subtitle);

  } else {
    showError("noChart");
  }
  return showError();
}


function generatePieChart(data,chart_title,chart_subtitle){

  var plotOptions = {
    pie: {
      allowPointSelect: true,
      cursor: 'pointer',
      dataLabels: {
        enabled: true,
        format: '<b>{point.name}</b>: {point.percentage:.1f} %'
      },
      showInLegend: true
    }
  };

  var title = {
    text: chart_title
  };

  var subtitle = {
    text: chart_subtitle
  };

  var legend = {
    layout: 'vertical',
    align: 'right',
    verticalAlign: 'middle',
    borderWidth: 0
  };

  var series =  [
    {
      type: 'pie',
      name: 'entradas',
      colorByPoint: true,
      data: data
    }
  ];

  var json = {};
  json.plotOptions = plotOptions;
  json.title = title;
  json.subtitle = subtitle;
  json.legend = legend;
  json.series = series;

  $("#chart-container").highcharts(json);

}

function generateTest(){
Highcharts.chart('chart-container', {

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
}
