let allJobs = [];

async function loadJobs() {
  try {
    const res = await fetch("data/jobs.json");
    allJobs = await res.json();
  } catch (e) {
    allJobs = [];
  }
  render();
}

function chip(text, kind) {
  return `<span class="chip ${kind}">${text}</span>`;
}

function jobCard(job) {
  const scoreClass = job.match_score >= 60 ? "high" : "low";
  const matched = (job.matched_skills || []).map(s => chip(s, "matched")).join("");
  const missing = (job.missing_skills || []).map(s => chip(s, "missing")).join("");

  const resumeLink = job.resume_file
    ? `<a href="downloads/${job.resume_file}" download>Download resume</a>` : "";
  const coverLink = job.cover_letter_file
    ? `<a href="downloads/${job.cover_letter_file}" download>Download cover letter</a>` : "";

  return `
    <div class="card">
      <h2>${job.title}</h2>
      <div class="company">${job.company} - ${job.location}</div>
      <span class="score ${scoreClass}">${job.match_score}% match</span>
      <div class="chips">${matched}${missing}</div>
      <div class="actions">
        <a href="${job.url}" target="_blank" rel="noopener">View job</a>
        ${resumeLink}
        ${coverLink}
      </div>
    </div>`;
}

function render() {
  const minScore = Number(document.getElementById("min-score").value);
  const list = document.getElementById("job-list");
  const filtered = allJobs.filter(j => j.match_score >= minScore);

  list.innerHTML = filtered.length
    ? filtered.map(jobCard).join("")
    : "<p>No jobs at or above this match score yet.</p>";
}

document.getElementById("min-score").addEventListener("input", (e) => {
  document.getElementById("min-score-label").textContent = `${e.target.value}%`;
  render();
});

loadJobs();
