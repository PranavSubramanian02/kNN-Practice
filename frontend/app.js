// European Striker kNN Analytics Application Engine

// Global State
let analyticsData = null;
let allPlayers = [];
let currentBenchmark = "Kylian Mbappe";
let currentCompetitor = "Donyell Malen";
let lastComparisonData = null;
let currentTheme = localStorage.getItem("scout-theme") || "dark";

const radarInstances = {
  shooting: null,
  buildup: null,
  carrying: null,
  defending: null,
};
let pcaInstance = null;

// Theme Controller
function initTheme() {
  setTheme(currentTheme);

  const btnDark = document.getElementById("theme-btn-dark");
  const btnLight = document.getElementById("theme-btn-light");

  if (btnDark) {
    btnDark.addEventListener("click", () => setTheme("dark"));
  }
  if (btnLight) {
    btnLight.addEventListener("click", () => setTheme("light"));
  }
}

function setTheme(theme) {
  currentTheme = theme;
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("scout-theme", theme);

  const btnDark = document.getElementById("theme-btn-dark");
  const btnLight = document.getElementById("theme-btn-light");

  if (btnDark && btnLight) {
    const isDark = theme === "dark";
    btnDark.classList.toggle("active", isDark);
    btnDark.setAttribute("aria-pressed", isDark ? "true" : "false");
    btnLight.classList.toggle("active", !isDark);
    btnLight.setAttribute("aria-pressed", !isDark ? "true" : "false");
  }

  // Update Chart.js Defaults
  Chart.defaults.font.family = "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif";
  Chart.defaults.color = theme === "dark" ? "#94a3b8" : "#475569";

  // Re-render active charts with updated theme palette if data exists
  if (lastComparisonData) {
    renderRadars(
      lastComparisonData.category_radars,
      lastComparisonData.target.player,
      lastComparisonData.competitor.player,
    );
    renderPCA(
      lastComparisonData.pca_points,
      lastComparisonData.target.player,
      lastComparisonData.competitor.player,
    );
  }
}

// Name Normalization & Client-Side kNN Engine
function normalizeName(text) {
  if (typeof text !== "string") return "";
  return text
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[øØ]/g, "o")
    .replace(/[đĐ]/g, "d")
    .replace(/ß/g, "ss")
    .trim()
    .toLowerCase();
}

function roundTo(value, decimals) {
  const factor = 10 ** decimals;
  return Math.round((value + Number.EPSILON) * factor) / factor;
}

function findPlayerIndex(queryName) {
  const cleanQuery = normalizeName(queryName);
  const exactIdx = analyticsData.players.findIndex(
    (p) => p.search_name === cleanQuery,
  );
  if (exactIdx !== -1) return exactIdx;
  const partialIdx = analyticsData.players.findIndex((p) =>
    p.search_name.includes(cleanQuery),
  );
  if (partialIdx === -1) {
    throw new Error(`Player '${queryName}' was not found in dataset.`);
  }
  return partialIdx;
}

function computeComparison(competitorName, benchmarkName) {
  const { features, feature_labels: featureLabels, categories, players } = analyticsData;
  const targetIdx = findPlayerIndex(benchmarkName);
  const compIdx = findPlayerIndex(competitorName);
  const target = players[targetIdx];
  const comp = players[compIdx];

  const featureIndex = Object.fromEntries(features.map((f, i) => [f, i]));

  // Standardized Euclidean distance and per-feature z-score deltas
  let sumSq = 0;
  let closestIdx = 0;
  let farthestIdx = 0;
  const zDiffs = features.map((_, i) => {
    const diff = target.z[i] - comp.z[i];
    sumSq += diff * diff;
    return Math.abs(diff);
  });

  for (let i = 1; i < zDiffs.length; i++) {
    if (zDiffs[i] < zDiffs[closestIdx]) closestIdx = i;
    if (zDiffs[i] > zDiffs[farthestIdx]) farthestIdx = i;
  }

  const dist = Math.sqrt(sumSq);
  const simPct = (1.0 / (1.0 + dist)) * 100;

  const buildExtremeMetric = (idx) => {
    const feat = features[idx];
    return {
      feature: feat,
      label: featureLabels[feat] || feat,
      z_diff: roundTo(zDiffs[idx], 3),
      target_val: roundTo(target.raw[idx], 2),
      comp_val: roundTo(comp.raw[idx], 2),
    };
  };

  const categoryRadars = {};
  const comparisonTable = [];

  for (const cat of categories) {
    categoryRadars[cat.name] = {
      labels: cat.features.map((f) => featureLabels[f] || f),
      features: cat.features,
      target_scores: cat.features.map((f) => target.pct[featureIndex[f]]),
      competitor_scores: cat.features.map((f) => comp.pct[featureIndex[f]]),
      target_raw: cat.features.map((f) => roundTo(target.raw[featureIndex[f]], 2)),
      competitor_raw: cat.features.map((f) => roundTo(comp.raw[featureIndex[f]], 2)),
    };

    for (const f of cat.features) {
      const idx = featureIndex[f];
      const tVal = target.raw[idx];
      const cVal = comp.raw[idx];
      comparisonTable.push({
        category: cat.name,
        feature: f,
        label: featureLabels[f] || f,
        target_value: roundTo(tVal, 2),
        competitor_value: roundTo(cVal, 2),
        raw_diff: roundTo(tVal - cVal, 2),
        z_diff: roundTo(zDiffs[idx], 3),
        advantage: tVal > cVal ? "target" : cVal > tVal ? "competitor" : "equal",
      });
    }
  }

  const pcaPoints = players.map((p, idx) => ({
    player: p.player,
    club: p.club,
    league: p.league,
    x: p.pca[0],
    y: p.pca[1],
    is_target: idx === targetIdx,
    is_competitor: idx === compIdx,
  }));

  const formatDossier = (p) => ({
    player: p.player,
    club: p.club,
    league: p.league,
    position: p.position,
    total_goals: p.total_goals,
    total_assists: p.total_assists,
    goals_per90: p.goals_per90,
    assists_per90: p.assists_per90,
  });

  return {
    target: formatDossier(target),
    competitor: formatDossier(comp),
    euclidean_distance: roundTo(dist, 4),
    similarity_percentage: roundTo(simPct, 1),
    closest_metric: buildExtremeMetric(closestIdx),
    farthest_metric: buildExtremeMetric(farthestIdx),
    category_radars: categoryRadars,
    comparison_table: comparisonTable,
    pca_points: pcaPoints,
  };
}

// Static Data Loading
async function fetchPlayers() {
  try {
    const res = await fetch("./data.json");
    if (!res.ok) throw new Error("Failed to load static dataset");
    analyticsData = await res.json();
    currentBenchmark = analyticsData.default_benchmark || currentBenchmark;
    allPlayers = analyticsData.players.map((p) => ({
      name: p.player,
      searchName: p.search_name,
      club: p.club,
      league: p.league,
      position: p.position,
    }));
  } catch (err) {
    console.error("Error loading striker dataset:", err);
  }
}

async function fetchComparison(
  competitorName,
  benchmarkName = currentBenchmark,
) {
  try {
    if (!analyticsData) return;
    const data = computeComparison(competitorName, benchmarkName);

    lastComparisonData = data;
    currentBenchmark = data.target.player;
    currentCompetitor = data.competitor.player;

    updateUI(data);
  } catch (err) {
    console.error("Error computing striker comparison:", err);
  }
}

// UI Updating
function updateUI(data) {
  // Update Player Banner
  document.getElementById("target-name").textContent = data.target.player;
  document.getElementById("target-meta").textContent =
    `${data.target.club} • ${data.target.league} • ${data.target.position}`;

  document.getElementById("comp-name").textContent = data.competitor.player;
  document.getElementById("comp-meta").textContent =
    `${data.competitor.club} • ${data.competitor.league} • ${data.competitor.position}`;

  const targetGoals =
    data.target && (data.target.total_goals ?? data.target.goals) !== undefined
      ? (data.target.total_goals ?? data.target.goals)
      : 17;
  const targetAssists =
    data.target && (data.target.total_assists ?? data.target.assists) !== undefined
      ? (data.target.total_assists ?? data.target.assists)
      : 3;
  const compGoals =
    data.competitor && (data.competitor.total_goals ?? data.competitor.goals) !== undefined
      ? (data.competitor.total_goals ?? data.competitor.goals)
      : "-";
  const compAssists =
    data.competitor && (data.competitor.total_assists ?? data.competitor.assists) !== undefined
      ? (data.competitor.total_assists ?? data.competitor.assists)
      : "-";

  const elTargetGoals = document.getElementById("target-goals");
  const elTargetAssists = document.getElementById("target-assists");
  const elCompGoals = document.getElementById("comp-goals");
  const elCompAssists = document.getElementById("comp-assists");

  if (elTargetGoals) elTargetGoals.textContent = targetGoals;
  if (elTargetAssists) elTargetAssists.textContent = targetAssists;
  if (elCompGoals) elCompGoals.textContent = compGoals;
  if (elCompAssists) elCompAssists.textContent = compAssists;

  document.getElementById("th-target").textContent = data.target.player;
  document.getElementById("th-comp").textContent = data.competitor.player;

  // Update Summary KPI Cards
  document.getElementById("val-distance").textContent =
    data.euclidean_distance.toFixed(4);
  document.getElementById("val-similarity").textContent =
    `${data.similarity_percentage.toFixed(1)}%`;

  // Closest Playstyle Match (Clean metric name only - bottom details omitted per user instruction)
  const elClosestLabel = document.getElementById("val-closest-label");
  if (elClosestLabel) elClosestLabel.textContent = data.closest_metric.label;

  // Biggest Tactical Contrast (Clean metric name only - bottom details omitted per user instruction)
  const elFarthestLabel = document.getElementById("val-farthest-label");
  if (elFarthestLabel) elFarthestLabel.textContent = data.farthest_metric.label;

  // Render Charts
  renderRadars(
    data.category_radars,
    data.target.player,
    data.competitor.player,
  );
  renderPCA(data.pca_points, data.target.player, data.competitor.player);

  // Render Comparison Table
  renderTable(data.comparison_table);

  // Update Quick Select Active State
  document.querySelectorAll(".pill-btn").forEach((btn) => {
    btn.classList.toggle(
      "active",
      btn.dataset.player === data.competitor.player,
    );
  });
}

// Radar Label Formatting for Multi-line Presentation
function formatRadarLabel(label) {
  if (Array.isArray(label)) return label;
  const labelMap = {
    "Expected Goals (xG) / 90": ["Expected Goals (xG)", "/ 90"],
    "Non-Penalty Expected Goals (npxG) / 90": ["Non-Penalty xG", "(npxG) / 90"],
    "Post-Shot Expected Goals (PSxG) / 90": ["Post-Shot xG", "(PSxG) / 90"],
    "Shot Conversion Rate (%)": ["Shot Conversion", "Rate (%)"],
    "Shots on Target / 90": ["Shots on Target", "/ 90"],
    "Expected Assists (xA) / 90": ["Expected Assists", "(xA) / 90"],
    "Shot-Creating Actions (SCA) / 90": ["Shot-Creating", "Actions (SCA) / 90"],
    "Progressive Passes Received / 90": ["Progressive Passes", "Received / 90"],
    "Pass Completion Rate Under Pressure (%)": ["Pass Completion Under", "Pressure (%)"],
    "Progressive Carries / 90": ["Progressive Carries", "/ 90"],
    "Successful Take-on Rate (%)": ["Successful Take-on", "Rate (%)"],
    "Touches in Attacking Penalty Area / 90": ["Touches in Attacking", "Penalty Area / 90"],
    "Tackles & Interceptions in Attacking 3rd / 90": ["Tackles & Interceptions", "in Attacking 3rd / 90"],
    "Ball Recoveries / 90": ["Ball Recoveries", "/ 90"],
    "Aerial Duels Won (%)": ["Aerial Duels", "Won (%)"],
  };

  if (labelMap[label]) return labelMap[label];

  if (typeof label === "string" && label.length > 18) {
    const words = label.split(" ");
    const mid = Math.ceil(words.length / 2);
    return [words.slice(0, mid).join(" "), words.slice(mid).join(" ")];
  }
  return label;
}

// Chart.js Category Radars
function createRadarChart(
  canvasId,
  labels,
  targetScores,
  compScores,
  targetName,
  compName,
) {
  const ctx = document.getElementById(canvasId).getContext("2d");
  const formattedLabels = labels.map(formatRadarLabel);

  const isDark = currentTheme === "dark";
  const gridColor = isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(15, 23, 42, 0.08)";
  const labelColor = isDark ? "#cbd5e1" : "#334155";

  return new Chart(ctx, {
    type: "radar",
    data: {
      labels: formattedLabels,
      datasets: [
        {
          label: targetName,
          data: targetScores,
          borderColor: isDark ? "#ef4444" : "#dc2626",
          backgroundColor: isDark ? "rgba(239, 68, 68, 0.22)" : "rgba(220, 38, 38, 0.18)",
          borderWidth: 2,
          pointBackgroundColor: isDark ? "#ef4444" : "#dc2626",
          pointRadius: 3,
        },
        {
          label: compName,
          data: compScores,
          borderColor: isDark ? "#3b82f6" : "#2563eb",
          backgroundColor: isDark ? "rgba(59, 130, 246, 0.22)" : "rgba(37, 99, 235, 0.18)",
          borderWidth: 2,
          pointBackgroundColor: isDark ? "#3b82f6" : "#2563eb",
          pointRadius: 3,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          min: 0,
          max: 100,
          ticks: { display: false, stepSize: 25 },
          grid: { color: gridColor },
          angleLines: { color: gridColor },
          pointLabels: {
            color: labelColor,
            font: { size: 9.5, weight: "600", family: "'Plus Jakarta Sans', sans-serif" },
            padding: 6,
          },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#0f172a",
          titleColor: "#f8fafc",
          bodyColor: "#cbd5e1",
          borderColor: "rgba(255, 255, 255, 0.15)",
          borderWidth: 1,
          padding: 8,
          cornerRadius: 6,
          callbacks: {
            title: (items) => {
              const label = items[0].label;
              return Array.isArray(label) ? label.join(" ") : label;
            },
            label: (ctx) => ` ${ctx.dataset.label}: ${ctx.raw}th percentile`,
          },
        },
      },
    },
  });
}

function renderRadars(radarsData, targetName, compName) {
  const mapping = [
    {
      key: "Shooting Efficiency & Shot Quality",
      id: "radarShooting",
      instanceKey: "shooting",
    },
    {
      key: "Build-up Play & Creative Linkage",
      id: "radarBuildup",
      instanceKey: "buildup",
    },
    {
      key: "Ball Carrying & Space Creation",
      id: "radarCarrying",
      instanceKey: "carrying",
    },
    {
      key: "Defensive Work Rate & Pressing",
      id: "radarDefending",
      instanceKey: "defending",
    },
  ];

  mapping.forEach((item) => {
    if (radarInstances[item.instanceKey]) {
      radarInstances[item.instanceKey].destroy();
    }
    const catData = radarsData[item.key];
    if (catData) {
      radarInstances[item.instanceKey] = createRadarChart(
        item.id,
        catData.labels,
        catData.target_scores,
        catData.competitor_scores,
        targetName,
        compName,
      );
    }
  });
}

// Chart.js 2D PCA Scatter
function renderPCA(pcaPoints, targetName, compName) {
  if (pcaInstance) {
    pcaInstance.destroy();
  }

  const targetPoint = pcaPoints.find((p) => p.is_target);
  const compPoint = pcaPoints.find((p) => p.is_competitor);
  const otherPoints = pcaPoints.filter((p) => !p.is_target && !p.is_competitor);

  const isDark = currentTheme === "dark";
  const axisColor = isDark ? "#94a3b8" : "#475569";
  const gridColor = isDark ? "rgba(255, 255, 255, 0.06)" : "rgba(15, 23, 42, 0.06)";
  const otherPointsBg = isDark ? "rgba(148, 163, 184, 0.45)" : "rgba(100, 116, 139, 0.4)";

  const ctx = document.getElementById("pcaChart").getContext("2d");

  pcaInstance = new Chart(ctx, {
    type: "scatter",
    data: {
      datasets: [
        {
          label: targetName,
          data: targetPoint
            ? [{ x: targetPoint.x, y: targetPoint.y, raw: targetPoint }]
            : [],
          backgroundColor: isDark ? "#ef4444" : "#dc2626",
          borderColor: "#ffffff",
          borderWidth: 2,
          pointRadius: 9,
          pointHoverRadius: 11,
          order: 1,
        },
        {
          label: compName,
          data: compPoint
            ? [{ x: compPoint.x, y: compPoint.y, raw: compPoint }]
            : [],
          backgroundColor: isDark ? "#3b82f6" : "#2563eb",
          borderColor: "#ffffff",
          borderWidth: 2,
          pointRadius: 9,
          pointHoverRadius: 11,
          order: 2,
        },
        {
          label: "Other European Strikers",
          data: otherPoints.map((p) => ({ x: p.x, y: p.y, raw: p })),
          backgroundColor: otherPointsBg,
          borderColor: "transparent",
          pointRadius: 4,
          pointHoverRadius: 6,
          order: 3,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          title: {
            display: true,
            text: "Principal Component 1 (PC1) — Offensive Volume & Penetration",
            color: axisColor,
            font: { size: 11, weight: "600", family: "'Plus Jakarta Sans', sans-serif" },
          },
          grid: { color: gridColor },
          ticks: { color: axisColor },
        },
        y: {
          title: {
            display: true,
            text: "Principal Component 2 (PC2) — Creative Linkage vs Box Finishing",
            color: axisColor,
            font: { size: 11, weight: "600", family: "'Plus Jakarta Sans', sans-serif" },
          },
          grid: { color: gridColor },
          ticks: { color: axisColor },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#0f172a",
          titleColor: "#f8fafc",
          bodyColor: "#cbd5e1",
          borderColor: "rgba(255, 255, 255, 0.15)",
          borderWidth: 1,
          padding: 10,
          cornerRadius: 8,
          callbacks: {
            title: (items) => {
              const item = items[0];
              const p = item.raw.raw;
              return `${p.player} (${p.club})`;
            },
            label: (item) => {
              const p = item.raw.raw;
              return `League: ${p.league} | PC1: ${p.x.toFixed(2)}, PC2: ${p.y.toFixed(2)}`;
            },
          },
        },
      },
    },
  });

  // Update Legend Labels
  document.getElementById("pca-legend-target").textContent = targetName;
  document.getElementById("pca-legend-comp").textContent = compName;
}

// 15-Metric Comparison Table
function renderTable(rows) {
  const tbody = document.getElementById("comparison-table-body");
  tbody.innerHTML = "";

  rows.forEach((row) => {
    const tr = document.createElement("tr");

    let advantageClass = "advantage-equal";
    let advantageText = "Equal";

    if (row.advantage === "target") {
      advantageClass = "advantage-target";
      advantageText = `${currentBenchmark.split(" ").pop()} +`;
    } else if (row.advantage === "competitor") {
      advantageClass = "advantage-comp";
      advantageText = `${currentCompetitor.split(" ").pop()} +`;
    }

    const diffFormatted =
      row.raw_diff > 0
        ? `+${row.raw_diff.toFixed(2)}`
        : row.raw_diff.toFixed(2);

    tr.innerHTML = `
      <td><strong>${row.label}</strong></td>
      <td><span class="category-tag">${row.category}</span></td>
      <td class="stat-val-target">${row.target_value.toFixed(2)}</td>
      <td class="stat-val-comp">${row.competitor_value.toFixed(2)}</td>
      <td>${diffFormatted}</td>
      <td><span class="advantage-badge ${advantageClass}">${advantageText}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

// Search and Autocomplete
function setupSearch() {
  const searchInput = document.getElementById("striker-search");
  const dropdown = document.getElementById("autocomplete-list");

  searchInput.addEventListener("input", () => {
    const query = normalizeName(searchInput.value);
    dropdown.innerHTML = "";

    if (!query) {
      dropdown.style.display = "none";
      return;
    }

    const matches = allPlayers
      .filter(
        (p) =>
          p.searchName.includes(query) ||
          normalizeName(p.club).includes(query),
      )
      .slice(0, 8);

    if (matches.length === 0) {
      dropdown.style.display = "none";
      return;
    }

    matches.forEach((player) => {
      const div = document.createElement("div");
      div.className = "autocomplete-item";
      div.innerHTML = `
        <span class="item-name">${player.name}</span>
        <span class="item-meta">${player.club} • ${player.league}</span>
      `;
      div.addEventListener("click", () => {
        searchInput.value = player.name;
        dropdown.style.display = "none";
        fetchComparison(player.name);
      });
      dropdown.appendChild(div);
    });

    dropdown.style.display = "block";
  });

  // Hide dropdown on outside click
  document.addEventListener("click", (e) => {
    if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.style.display = "none";
    }
  });

  // Quick Select Pills
  document.querySelectorAll(".pill-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const playerName = btn.dataset.player;
      searchInput.value = playerName;
      dropdown.style.display = "none";
      fetchComparison(playerName);
    });
  });
}

// Initialization
document.addEventListener("DOMContentLoaded", async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const themeParam = urlParams.get("theme");
  if (themeParam === "light" || themeParam === "dark") {
    currentTheme = themeParam;
  }
  initTheme();
  await fetchPlayers();
  setupSearch();
  const initialPlayer = urlParams.get("player") || "Donyell Malen";
  await fetchComparison(initialPlayer);
});
