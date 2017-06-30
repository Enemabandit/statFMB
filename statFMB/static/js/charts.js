
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
  clearError();
  clearChart();
  var chartContainer = document.getElementById("chart-container");

  if (document.getElementById("maps-world").checked){
    chartContainer.innerHTML = Date();
  } else if (document.getElementById("maps-europe").checked){
    chartContainer.innerHTML = Date();
  } else if (document.getElementById("maps-portugal").checked){
    chartContainer.innerHTML = Date();
  } else {
    showError("noChart");
  }
}

function generatePie(){
  clearError();
  clearChart();
  var chartContainer = document.getElementById("chart-container");

  if (document.getElementById("pie-gates").checked){
    chartContainer.innerHTML = Date();
  } else if (document.getElementById("pie-countries").checked){
    chartContainer.innerHTML = Date();
  } else if (document.getElementById("pie-municipalities").checked){
    chartContainer.innerHTML = Date();
  } else {
    showError("noChart");
  }
}
