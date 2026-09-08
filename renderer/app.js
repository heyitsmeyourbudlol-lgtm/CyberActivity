const ACTORS = [
  { id: null, label: "All activity", short: "ALL", color: "#171c21" },
  { id: "russia", label: "Russia", short: "RU", color: "var(--russia)" },
  { id: "china", label: "China", short: "CN", color: "var(--china)" },
  { id: "northKorea", label: "North Korea", short: "NK", color: "var(--nk)" },
  { id: "adversarialAI", label: "Adversarial AI", short: "AI", color: "var(--ai)" },
  {
    id: "digitalSovereignty",
    label: "Digital Sovereignty",
    short: "SOV",
    color: "var(--sov)",
  },
];

const SOURCE_DEFS = [
  { id: "theRecord", name: "The Record" },
  { id: "lawfare", name: "Lawfare" },
  { id: "krebs", name: "Krebs on Security" },
  { id: "googleLawfare", name: "Lawfare via Google News" },
  { id: "googleStateCyber", name: "State cyber watch" },
];

const state = {
  articles: [],
  beats: {},
  articleSummaries: {},
  summary: "Pulling the landscape…",
  summaryModel: null,
  summaryProvider: null,
  refreshedAt: null,
  selectedActor: null,
  enabledSources: new Set(SOURCE_DEFS.map((s) => s.id)),
  loading: false,
  activeArticleId: null,
};

const els = {
  actorNav: document.getElementById("actor-nav"),
  sourceToggles: document.getElementById("source-toggles"),
  refreshBtn: document.getElementById("refresh-btn"),
  summaryText: document.getElementById("summary-text"),
  summaryModel: document.getElementById("summary-model"),
  refreshedAt: document.getElementById("refreshed-at"),
  posterGrid: document.getElementById("poster-grid"),
  actorBoard: document.getElementById("actor-board"),
  errorLine: document.getElementById("error-line"),
  modal: document.getElementById("article-modal"),
  modalTitle: document.getElementById("modal-title"),
  modalSource: document.getElementById("modal-source"),
  modalDate: document.getElementById("modal-date"),
  modalBrandChip: document.getElementById("modal-brand-chip"),
  modalTags: document.getElementById("modal-tags"),
  modalSummary: document.getElementById("modal-summary"),
  modalModel: document.getElementById("modal-model"),
  modalOpen: document.getElementById("modal-open"),
  modalClarifyInput: document.getElementById("modal-clarify-input"),
  modalClarifyAsk: document.getElementById("modal-clarify-ask"),
  modalClarifyAnswer: document.getElementById("modal-clarify-answer"),
  modalClarifyModel: document.getElementById("modal-clarify-model"),
};

function actorMeta(id) {
  return ACTORS.find((a) => a.id === id) || ACTORS[0];
}

function accent(id) {
  return (
    {
      russia: "#2e5c9e",
      china: "#b82e2e",
      northKorea: "#6b478c",
      adversarialAI: "#267a6b",
      digitalSovereignty: "#7a6138",
      general: "#38454f",
    }[id] || "#38454f"
  );
}

function shortLabel(id) {
  return actorMeta(id)?.short || "ALL";
}

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
}

function formatDay(iso) {
  try {
    return new Date(iso).toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return "";
  }
}

function filteredArticles() {
  if (!state.selectedActor) return state.articles;
  return state.articles.filter((a) => a.actors.includes(state.selectedActor));
}

function renderNav() {
  els.actorNav.innerHTML = ACTORS.map((actor) => {
    const count = actor.id
      ? state.articles.filter((a) => a.actors.includes(actor.id)).length
      : state.articles.length;
    const active =
      state.selectedActor === actor.id || (!actor.id && state.selectedActor == null);
    return `<button class="actor-btn ${active ? "active" : ""}" data-actor="${actor.id ?? ""}">
      <span class="dot" style="background:${actor.color}"></span>
      <span>${actor.label}</span>
      <span class="count">${count}</span>
    </button>`;
  }).join("");

  els.actorNav.querySelectorAll(".actor-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const raw = btn.getAttribute("data-actor");
      state.selectedActor = raw === "" ? null : raw;
      render();
    });
  });
}

function renderSources() {
  els.sourceToggles.innerHTML = SOURCE_DEFS.map(
    (s) => `<label>
      <input type="checkbox" data-source="${s.id}" ${
      state.enabledSources.has(s.id) ? "checked" : ""
    } />
      <span>${s.name}</span>
    </label>`
  ).join("");

  els.sourceToggles.querySelectorAll("input").forEach((input) => {
    input.addEventListener("change", () => {
      const id = input.getAttribute("data-source");
      if (input.checked) state.enabledSources.add(id);
      else state.enabledSources.delete(id);
    });
  });
}

function renderPosters() {
  const items = filteredArticles().slice(0, 24);
  if (!items.length) {
    els.posterGrid.innerHTML = `<p class="quiet">No articles yet. Hit Refresh.</p>`;
    return;
  }

  els.posterGrid.innerHTML = items
    .map((article, index) => {
      const color = accent(article.primaryActor);
      const beat = state.beats[article.id] || article.summary || article.title;
      const cats = (article.categories || []).slice(0, 2).join(" · ").toUpperCase();
      const tags = article.actors
        .slice(0, 3)
        .map(
          (a) =>
            `<span class="tag" style="background:${accent(a)}22;color:${accent(a)}">${shortLabel(
              a
            )}</span>`
        )
        .join("");

      return `<article class="poster" data-id="${escapeHtml(article.id)}" style="animation-delay:${
        index * 30
      }ms">
        <div class="poster-masthead">
          <div class="brand-chip" style="background:${color}">${article.brand}</div>
          <div class="mast-copy">
            <strong>${article.sourceName.toUpperCase()}</strong>
            <span>${cats || "CYBER WATCH"}</span>
          </div>
        </div>
        <div class="poster-hero" style="background:linear-gradient(135deg, ${color}f2, #171c21d9)">
          <div class="watermark">${shortLabel(article.primaryActor)}</div>
          <h3>${escapeHtml(article.title)}</h3>
        </div>
        <div class="poster-body">
          <p>${escapeHtml(beat)}</p>
          <div class="tags">${tags}</div>
        </div>
        <div class="poster-foot">
          <span>${formatDay(article.publishedAt)}</span>
          <button type="button" class="open" data-open-original="${escapeHtml(article.url)}">Open original →</button>
        </div>
      </article>`;
    })
    .join("");

  els.posterGrid.querySelectorAll(".poster").forEach((node) => {
    node.addEventListener("click", (event) => {
      const openBtn = event.target.closest("[data-open-original]");
      if (openBtn) {
        event.stopPropagation();
        const url = openBtn.getAttribute("data-open-original");
        if (url) window.cyberactivity.openExternal(url);
        return;
      }
      const id = node.getAttribute("data-id");
      const article = state.articles.find((a) => a.id === id);
      if (article) openArticleModal(article);
    });
  });
}

function closeArticleModal() {
  state.activeArticleId = null;
  els.modalClarifyInput.value = "";
  els.modalClarifyAnswer.textContent = "";
  els.modalClarifyModel.textContent = "";
  els.modalClarifyAsk.disabled = false;
  els.modal.classList.add("hidden");
  els.modal.setAttribute("aria-hidden", "true");
}

async function askArticleClarification() {
  const article = state.articles.find((a) => a.id === state.activeArticleId);
  if (!article) return;
  const question = els.modalClarifyInput.value.trim();
  if (!question) {
    els.modalClarifyAnswer.textContent = "Type a short question first.";
    els.modalClarifyModel.textContent = "";
    return;
  }

  els.modalClarifyAsk.disabled = true;
  els.modalClarifyAnswer.textContent = "Thinking with cyber model…";
  els.modalClarifyModel.textContent = "DeepHat/DeepHat-V1-7B · local";
  try {
    const summaryText = state.articleSummaries[article.id]?.text || "";
    const result = await window.cyberactivity.clarifyArticle({
      article,
      question,
      summaryText,
    });
    if (state.activeArticleId !== article.id) return;
    els.modalClarifyAnswer.textContent = result.text;
    els.modalClarifyModel.textContent = result.model
      ? `${result.model} · ${result.provider === "ollama" ? "local" : result.provider}`
      : result.provider || "";
  } catch (err) {
    if (state.activeArticleId !== article.id) return;
    els.modalClarifyAnswer.textContent = err?.message || "Clarification failed.";
    els.modalClarifyModel.textContent = "error";
  } finally {
    els.modalClarifyAsk.disabled = false;
  }
}

async function openArticleModal(article) {
  state.activeArticleId = article.id;
  const color = accent(article.primaryActor);
  els.modalBrandChip.textContent = article.brand;
  els.modalBrandChip.style.background = color;
  els.modalSource.textContent = article.sourceName.toUpperCase();
  els.modalDate.textContent = formatDate(article.publishedAt);
  els.modalTitle.textContent = article.title;
  els.modalTags.innerHTML = article.actors
    .slice(0, 4)
    .map(
      (a) =>
        `<span class="tag" style="background:${accent(a)}22;color:${accent(a)}">${shortLabel(a)}</span>`
    )
    .join("");
  els.modalOpen.onclick = () => window.cyberactivity.openExternal(article.url);
  els.modalClarifyInput.value = "";
  els.modalClarifyAnswer.textContent = "";
  els.modalClarifyModel.textContent = "";

  const cached = state.articleSummaries[article.id];
  if (cached) {
    els.modalSummary.textContent = cached.text;
    els.modalModel.textContent = cached.model
      ? `${cached.model} · ${cached.provider === "ollama" ? "local" : cached.provider}`
      : cached.provider || "";
  } else {
    els.modalSummary.textContent = "Generating high-level summary…";
    els.modalModel.textContent = "QyrouNnet/summarizer:400m · local";
  }

  els.modal.classList.remove("hidden");
  els.modal.setAttribute("aria-hidden", "false");

  if (cached) return;

  try {
    const result = await window.cyberactivity.summarizeArticle(article);
    if (state.activeArticleId !== article.id) return;
    state.articleSummaries[article.id] = result;
    els.modalSummary.textContent = result.text;
    els.modalModel.textContent = result.model
      ? `${result.model} · ${result.provider === "ollama" ? "local" : result.provider}`
      : result.provider || "";
  } catch (err) {
    if (state.activeArticleId !== article.id) return;
    els.modalSummary.textContent =
      article.summary || "Could not generate a summary. Try Open original.";
    els.modalModel.textContent = err?.message || "summary failed";
  }
}

function renderBoard() {
  const boardActors = ACTORS.filter((a) => a.id);
  els.actorBoard.innerHTML = boardActors
    .map((actor) => {
      const items = state.articles.filter((a) => a.actors.includes(actor.id));
      const list = items.length
        ? `<ul>${items
            .slice(0, 3)
            .map((a) => `<li>${escapeHtml(a.title)}</li>`)
            .join("")}</ul>`
        : `<p class="quiet">Quiet this cycle</p>`;
      return `<div class="actor-card" style="border-color:${accent(actor.id)}59">
        <div style="display:flex;justify-content:space-between">
          <span class="code" style="color:${accent(actor.id)}">${actor.short}</span>
          <span class="mono">${items.length}</span>
        </div>
        <h3>${actor.label}</h3>
        ${list}
      </div>`;
    })
    .join("");
}

function escapeHtml(str) {
  return String(str || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function render() {
  els.summaryText.textContent = state.summary;
  if (state.summaryModel) {
    const via = state.summaryProvider === "ollama" ? "local" : state.summaryProvider || "model";
    els.summaryModel.textContent = `${state.summaryModel} · ${via}`;
  } else if (state.summaryProvider === "extractive") {
    els.summaryModel.textContent = "extractive fallback";
  } else {
    els.summaryModel.textContent = "";
  }
  els.refreshedAt.textContent = state.refreshedAt ? formatDate(state.refreshedAt) : "";
  renderNav();
  renderPosters();
  renderBoard();
}

async function refresh() {
  if (state.loading) return;
  state.loading = true;
  els.refreshBtn.disabled = true;
  els.refreshBtn.textContent = "Refreshing";
  els.errorLine.classList.add("hidden");
  try {
    const result = await window.cyberactivity.refresh([...state.enabledSources]);
    state.articles = result.articles || [];
    state.summary = result.executiveSummary || state.summary;
    state.summaryModel = result.summaryModel || null;
    state.summaryProvider = result.summaryProvider || null;
    state.beats = result.beats || {};
    state.refreshedAt = result.refreshedAt;
    if (!state.articles.length) {
      els.errorLine.textContent =
        "Feeds returned nothing (some sources block automated clients). Try again shortly.";
      els.errorLine.classList.remove("hidden");
    }
    localStorage.setItem(
      "cyberactivity.cache",
      JSON.stringify({
        articles: state.articles,
        summary: state.summary,
        summaryModel: state.summaryModel,
        summaryProvider: state.summaryProvider,
        beats: state.beats,
        refreshedAt: state.refreshedAt,
      })
    );
    render();
  } catch (err) {
    els.errorLine.textContent = err?.message || "Refresh failed.";
    els.errorLine.classList.remove("hidden");
  } finally {
    state.loading = false;
    els.refreshBtn.disabled = false;
    els.refreshBtn.textContent = "Refresh";
  }
}

function loadCache() {
  try {
    const raw = localStorage.getItem("cyberactivity.cache");
    if (!raw) return;
    const cache = JSON.parse(raw);
    state.articles = cache.articles || [];
    state.summary = cache.summary || state.summary;
    state.summaryModel = cache.summaryModel || null;
    state.summaryProvider = cache.summaryProvider || null;
    state.beats = cache.beats || {};
    state.refreshedAt = cache.refreshedAt || null;
  } catch {
    // ignore
  }
}

els.refreshBtn.addEventListener("click", refresh);

els.modalClarifyAsk.addEventListener("click", askArticleClarification);
els.modalClarifyInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    askArticleClarification();
  }
});

els.modal.querySelectorAll("[data-close-modal]").forEach((node) => {
  node.addEventListener("click", closeArticleModal);
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !els.modal.classList.contains("hidden")) {
    closeArticleModal();
  }
});

renderSources();
loadCache();
render();
refresh();
