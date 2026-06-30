const dataPath = "../data/flipkart_products.csv";

const currency = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

function parseCsv(csvText) {
  const [headerLine, ...lines] = csvText.trim().split(/\r?\n/);
  const headers = headerLine.split(",");

  return lines.map((line) => {
    const values = line.split(",");
    const row = {};
    headers.forEach((header, index) => {
      row[header] = values[index];
    });

    row.actual_price = Number(row.actual_price);
    row.discounted_price = Number(row.discounted_price);
    row.discount_percentage = Number(row.discount_percentage);
    row.rating = Number(row.rating);
    row.rating_count = Number(row.rating_count);
    row.value_score =
      row.rating * 20 +
      row.discount_percentage * 0.6 +
      (row.rating_count / 100000) * 20;

    return row;
  });
}

function average(rows, field) {
  if (!rows.length) return 0;
  return rows.reduce((total, row) => total + row[field], 0) / rows.length;
}

function groupByCategory(rows, field) {
  const grouped = {};

  rows.forEach((row) => {
    if (!grouped[row.category]) grouped[row.category] = [];
    grouped[row.category].push(row[field]);
  });

  return Object.entries(grouped)
    .map(([category, values]) => ({
      category,
      value: values.reduce((total, value) => total + value, 0) / values.length,
    }))
    .sort((a, b) => b.value - a.value);
}

function renderKpis(rows) {
  document.querySelector("#totalProducts").textContent = rows.length;
  document.querySelector("#avgPrice").textContent = currency.format(
    average(rows, "discounted_price")
  );
  document.querySelector("#avgDiscount").textContent = `${average(
    rows,
    "discount_percentage"
  ).toFixed(1)}%`;
  document.querySelector("#avgRating").textContent = average(rows, "rating").toFixed(1);
}

function renderDiscountChart(rows) {
  const chart = document.querySelector("#discountChart");
  const grouped = groupByCategory(rows, "discount_percentage");
  const maxValue = Math.max(...grouped.map((item) => item.value), 1);

  chart.innerHTML = grouped
    .map(
      (item) => `
        <div class="bar-row">
          <div class="bar-label">${item.category}</div>
          <div class="bar-track">
            <div class="bar-fill" style="width: ${(item.value / maxValue) * 100}%"></div>
          </div>
          <div class="bar-value">${item.value.toFixed(1)}%</div>
        </div>
      `
    )
    .join("");
}

function renderPriceMix(rows) {
  const actualPrice = average(rows, "actual_price");
  const discountedPrice = average(rows, "discounted_price");
  const savings = actualPrice - discountedPrice;

  document.querySelector("#priceMix").innerHTML = `
    <div class="price-card">
      <span>Average Actual Price</span>
      <strong>${currency.format(actualPrice)}</strong>
    </div>
    <div class="price-card discount">
      <span>Average Discounted Price</span>
      <strong>${currency.format(discountedPrice)}</strong>
    </div>
    <div class="price-card">
      <span>Average Customer Saving</span>
      <strong>${currency.format(savings)}</strong>
    </div>
  `;
}

function renderValueList(rows) {
  const topRows = [...rows].sort((a, b) => b.value_score - a.value_score).slice(0, 5);

  document.querySelector("#valueList").innerHTML = topRows
    .map(
      (row) => `
        <div class="value-item">
          <strong>${row.product_name}</strong>
          <span>${row.brand} | ${currency.format(row.discounted_price)} | ${
        row.discount_percentage
      }% off | ${row.rating} rating</span>
        </div>
      `
    )
    .join("");
}

function renderTable(rows) {
  const sortedRows = [...rows].sort((a, b) => b.value_score - a.value_score);

  document.querySelector("#productRows").innerHTML = sortedRows
    .map(
      (row) => `
        <tr>
          <td>${row.product_name}</td>
          <td>${row.category}</td>
          <td>${row.brand}</td>
          <td>${currency.format(row.discounted_price)}</td>
          <td>${row.discount_percentage}%</td>
          <td>${row.rating}</td>
        </tr>
      `
    )
    .join("");
}

function renderDashboard(rows) {
  renderKpis(rows);
  renderDiscountChart(rows);
  renderPriceMix(rows);
  renderValueList(rows);
  renderTable(rows);
}

function setupFilters(rows) {
  const categoryFilter = document.querySelector("#categoryFilter");
  const categories = [...new Set(rows.map((row) => row.category))].sort();

  categories.forEach((category) => {
    const option = document.createElement("option");
    option.value = category;
    option.textContent = category;
    categoryFilter.appendChild(option);
  });

  categoryFilter.addEventListener("change", () => {
    const selectedCategory = categoryFilter.value;
    const filteredRows =
      selectedCategory === "All"
        ? rows
        : rows.filter((row) => row.category === selectedCategory);

    renderDashboard(filteredRows);
  });
}

async function init() {
  const response = await fetch(dataPath);
  const csvText = await response.text();
  const rows = parseCsv(csvText);

  setupFilters(rows);
  renderDashboard(rows);
}

init().catch((error) => {
  document.body.innerHTML = `
    <main class="error-state">
      <h1>Dashboard could not load</h1>
      <p>${error.message}</p>
      <p>Run this dashboard using a local server, for example: python -m http.server 8000</p>
    </main>
  `;
});
