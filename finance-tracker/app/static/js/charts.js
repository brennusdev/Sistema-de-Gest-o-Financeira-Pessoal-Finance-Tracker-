const CORES_CATEGORIAS = ["#3F6C51", "#A6432D", "#C9A227", "#52584F", "#7A9B87", "#C97F6B", "#8B7BB8", "#4A6FA5"];

async function carregarGraficoCategorias() {
  const resposta = await fetch("/api/gastos-por-categoria");
  const dados = await resposta.json();
  const canvas = document.getElementById("graficoCategorias");
  const nota = document.getElementById("notaCategorias");

  if (!dados.labels.length) {
    canvas.hidden = true;
    nota.hidden = false;
    return;
  }

  new Chart(canvas, {
    type: "doughnut",
    data: {
      labels: dados.labels,
      datasets: [{
        data: dados.valores,
        backgroundColor: CORES_CATEGORIAS,
        borderColor: "#F6F4EE",
        borderWidth: 2,
      }],
    },
    options: {
      plugins: {
        legend: { position: "bottom", labels: { font: { family: "Inter", size: 11 }, padding: 12 } },
      },
    },
  });
}

async function carregarGraficoEvolucao() {
  const resposta = await fetch("/api/evolucao-mensal");
  const dados = await resposta.json();
  const canvas = document.getElementById("graficoEvolucao");

  new Chart(canvas, {
    type: "bar",
    data: {
      labels: dados.meses,
      datasets: [
        { label: "Receitas", data: dados.receitas, backgroundColor: "#3F6C51", borderRadius: 3 },
        { label: "Despesas", data: dados.despesas, backgroundColor: "#A6432D", borderRadius: 3 },
      ],
    },
    options: {
      plugins: {
        legend: { position: "bottom", labels: { font: { family: "Inter", size: 11 }, padding: 12 } },
      },
      scales: {
        y: { beginAtZero: true, grid: { color: "#D3CFC2" }, ticks: { font: { family: "IBM Plex Mono", size: 10 } } },
        x: { grid: { display: false }, ticks: { font: { family: "IBM Plex Mono", size: 10 } } },
      },
    },
  });
}

document.addEventListener("DOMContentLoaded", () => {
  carregarGraficoCategorias();
  carregarGraficoEvolucao();
});
