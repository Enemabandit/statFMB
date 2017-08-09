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
    $("#chart-container").text("Not Implemented yet!");
    return 0;
  } else if (document.getElementById("maps-europe").checked){
    $("#chart-container").text("Not Implemented yet!");
    return 0;
  } else if (document.getElementById("maps-portugal").checked){
    $("#chart-container").text("Not Implemented yet!");
    return 0;
  } else {
    showError("noChart");
  }
  return showError();
}

function get_pie_data(data_set, minimum_value){
  minimum_value = (typeof minimum_value !== 'undefined')? minimum_value : 100;
  var result = [];
  for(var key in data_set){
    if (data_set.hasOwnProperty(key)){
      if (data_set[key] >= minimum_value){
        result.push([key, data_set[key]]);
      }
    }
  }
  return result;
}

//TODO: fine tune graphs with options!!
function generatePie(search){
  var title;
  var subtitle;
  var data;

  if (document.getElementById("pie-gates").checked){
    title = "Top Portas";
    subtitle = "Viaturas por porta";
    data = get_pie_data(search.tops.gates,0);
    return generatePieChart(data,title,subtitle);

  } else if (document.getElementById("pie-countries").checked){
    title = "Top Países";
    subtitle = "Passageiros por país (+100 entradas)";
    data = get_pie_data(search.tops.countries);
    return generatePieChart(data,title,subtitle);

  } else if (document.getElementById("pie-municipalities").checked){
    title = "Top Concelhos";
    subtitle = "passageiros por concelho (+100 entradas)";
    data = get_pie_data(search.tops.municipalities);
    return generatePieChart(data,title,subtitle);

  } else {
    showError("noChart");
  }
  return showError();
}

//TODO: tooltips of municipalyties pie chart are not correct
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
    align: 'left',
    verticalAlign: 'middle',
    borderWidth: 0
  };

  var chart = {
    marginLeft: 10
  };

  var series =  [
    {
      type: 'pie',
      name: 'entradas',
      colorByPoint: true,
      data: data
    }
  ];

  var options = {};
  options.plotOptions = plotOptions;
  options.title = title;
  options.chart = chart;
  options.subtitle = subtitle;
  options.legend = legend;
  options.series = series;

  $("#chart-container").highcharts(options);
}

function get_line_data(period_list,period_key){
  var result = [];
  period_list.forEach(function (period){
    result.push(period[period_key]);
  });
  return result;
}

function get_categories(period_list){
  var category_list = [];
  var period_key = "designation";
  period_list.forEach(function (period){
    category_list.push(period[period_key]);
  });
  return category_list;
}

function get_series(name,data){
  return {
    name: name,
    data: data
  };
}

function generateLine(search){
  var period_list = search.period_list;
  var series = [];
  var categories = get_categories(period_list);
  var period_key;
  var series_name;

  if ($("#vehicles-chk").prop('checked')) {
    period_key = "vehicles";
    series_name = "Viaturas";
    series.push(get_series(series_name,get_line_data(period_list,period_key)));
  }
  if ($("#bikes-chk").prop('checked')) {
    period_key = "bikes";
    series_name = "Motos";
    series.push(get_series(series_name,get_line_data(period_list,period_key)));
  }
  if ($("#lightduty-chk").prop('checked')) {
    period_key = "lightduty";
    series_name = "Ligeiros";
    series.push(get_series(series_name,get_line_data(period_list,period_key)));
  }
  if ($("#lightdutyXL-chk").prop('checked')) {
    period_key = "lightdutyXL";
    series_name = "LigeirosXL";
    series.push(get_series(series_name,get_line_data(period_list,period_key)));
  }
  if ($("#caravans-chk").prop('checked')) {
    period_key = "caravans";
    series_name = "Caravanas";
    series.push(get_series(series_name,get_line_data(period_list,period_key)));
  }
  if ($("#busses-chk").prop('checked')) {
    period_key = "busses";
    series_name = "Autocarros";
    series.push(get_series(series_name,get_line_data(period_list,period_key)));
  }
  if ($("#persons-chk").prop('checked')) {
    period_key = "persons";
    series_name = "Pessoas";
    series.push(get_series(series_name,get_line_data(period_list,period_key)));
  }
  if ($("#pedestrians-chk").prop('checked')) {
    period_key = "pawns";
    series_name = "Peões";
    series.push(get_series(series_name,get_line_data(period_list,period_key)));
  }
  if ($("#bicicles-chk").prop('checked')) {
    period_key = "bicicles";
    series_name = "Bicicletas";
    series.push(get_series(series_name,get_line_data(period_list,period_key)));

  }
  if ($("#passengers-chk").prop('checked')) {
    period_key = "passengers";
    series_name = "Passageiros";
    series.push(get_series(series_name,get_line_data(period_list,period_key)));
  }

  generateLineChart(series,categories);
}

function generateLineChart(chart_series,chart_categories){
  var title = {
    text: "Entradas ao longo do tempo"
   };
   var subtitle = {
     text: "Análise de entradas num determidado período de tempo"
   };
   var xAxis = {
     categories: chart_categories,
     reversed: true
   };
   var yAxis = {
     title: {
       text: 'numero de entradas'
     },
     plotLines: [{
       value: 0,
       width: 1,
       color: '#808080'
     }]
   };

   var tooltip = {
   };

   var legend = {
     layout: 'vertical',
     align: 'right',
     verticalAlign: 'middle',
     borderWidth: 0
   };

   var series =  chart_series;

   var options = {};
   options.title = title;
   options.subtitle = subtitle;
   options.xAxis = xAxis;
   options.yAxis = yAxis;
   options.tooltip = tooltip;
   options.legend = legend;
   options.series = series;

   $('#chart-container').highcharts(options);
}
