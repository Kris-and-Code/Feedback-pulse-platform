async function postJson(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || `HTTP ${response.status}`);
  }
  return data;
}

function showOutput(data) {
  document.getElementById("output").textContent = JSON.stringify(data, null, 2);
}

export async function scrapeReviews(url) {
  const endpoint = url.toLowerCase().includes("amazon.")
    ? "/scrape-amazon"
    : "/scrape-review";
  return postJson(endpoint, { url });
}

export async function analyzeText(text, mode = "simple") {
  return postJson("/analyze-text", { text, mode });
}

document.getElementById("analyzeBtn").addEventListener("click", async () => {
  try {
    const text = document.getElementById("reviewText").value;
    const mode = document.getElementById("analyzeMode").value;
    showOutput(await analyzeText(text, mode));
  } catch (error) {
    showOutput({ error: error.message });
  }
});

document.getElementById("scrapeBtn").addEventListener("click", async () => {
  try {
    const url = document.getElementById("scrapeUrl").value;
    showOutput(await scrapeReviews(url));
  } catch (error) {
    showOutput({ error: error.message });
  }
});
