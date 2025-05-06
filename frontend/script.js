const API_BASE = "https://shl-assessment-production-9508.up.railway.app/";

async function getRecommendations() {
  const jobDesc = document.getElementById("job-description").value.trim();
  const table = document.getElementById("results-table");
  const tbody = table.querySelector("tbody");
  const loading = document.getElementById("loading");

  tbody.innerHTML = "";
  table.classList.add("hidden");

  if (!jobDesc) {
    alert("Please enter a job description!");
    return;
  }

  loading.classList.remove("hidden");

  try {
    const response = await fetch(`${API_BASE}/recommend`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ query: jobDesc })
    });

    const data = await response.json();
    const assessments = data.recommended_assessments;

    if (!assessments || assessments.length === 0) {
      tbody.innerHTML = "<tr><td colspan='6'>No recommendations found.</td></tr>";
    } else {
      assessments.forEach(item => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${item.test_type || "N/A"}</td>
          <td>${item.duration}</td>
          <td>${item.adaptive_support}</td>
          <td>${item.remote_support}</td>
          <td>${item.description.slice(0, 100)}...</td>
          <td><a href="${item.url}" target="_blank">View</a></td>
        `;
        tbody.appendChild(row);
      });
    }

    table.classList.remove("hidden");
  } catch (err) {
    console.error(err);
    tbody.innerHTML = "<tr><td colspan='6'>Error fetching data. Please try again.</td></tr>";
    table.classList.remove("hidden");
  } finally {
    loading.classList.add("hidden");
  }
}
