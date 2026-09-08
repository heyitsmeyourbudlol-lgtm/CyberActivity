const DEFAULT_MODEL = "QyrouNnet/summarizer:400m";
const CYBER_MODEL = "DeepHat/DeepHat-V1-7B";
const OLLAMA_BASE = process.env.OLLAMA_HOST || "http://127.0.0.1:11434";

function shorten(text, limit = 160) {
  const t = String(text || "").trim();
  if (t.length <= limit) return t;
  return `${t.slice(0, limit).trim()}…`;
}

function actorLabel(id) {
  return (
    {
      russia: "Russia",
      china: "China",
      northKorea: "North Korea",
      adversarialAI: "Adversarial AI",
      digitalSovereignty: "Digital Sovereignty",
      general: "Landscape",
    }[id] || id
  );
}

function configuredModel() {
  return process.env.CYBERACTIVITY_MODEL || DEFAULT_MODEL;
}

function configuredCyberModel() {
  return process.env.CYBERACTIVITY_CYBER_MODEL || CYBER_MODEL;
}

function briefBullets(articles) {
  return articles
    .slice(0, 12)
    .map(
      (a) =>
        `- [${a.brand}] ${a.title} — ${shorten(a.summary, 140)} · ${a.actors
          .map(actorLabel)
          .join("/")}`
    )
    .join("\n");
}

async function ollamaChat(messages, { temperature = 0.3, model = configuredModel() } = {}) {
  const res = await fetch(`${OLLAMA_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model,
      messages,
      stream: false,
      options: { temperature },
    }),
  });
  if (!res.ok) {
    const errText = await res.text().catch(() => "");
    throw new Error(`Ollama ${res.status}: ${errText.slice(0, 200)}`);
  }
  const json = await res.json();
  const text = json?.message?.content?.trim();
  if (!text) throw new Error("Empty Ollama response");
  return { text, model, provider: "ollama" };
}

async function cloudChat(messages, { temperature = 0.3 } = {}) {
  const key = process.env.OPENAI_API_KEY || process.env.CYBERACTIVITY_API_KEY;
  if (!key) return null;
  const base = process.env.OPENAI_BASE_URL || "https://api.openai.com/v1";
  const model = process.env.CYBERACTIVITY_CLOUD_MODEL || "gpt-4o-mini";
  const res = await fetch(`${base}/chat/completions`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${key}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ model, temperature, messages }),
  });
  if (!res.ok) return null;
  const json = await res.json();
  const text = json?.choices?.[0]?.message?.content?.trim();
  if (!text) return null;
  return { text, model, provider: "cloud" };
}

async function generate(messages, { temperature = 0.3 } = {}) {
  // Summarizer path: local Ollama QyrouNnet/summarizer:400m. Optional cloud override if keys exist.
  try {
    return await ollamaChat(messages, { temperature, model: configuredModel() });
  } catch {
    const cloud = await cloudChat(messages, { temperature });
    if (cloud) return cloud;
    throw new Error("Summarizer unavailable");
  }
}

async function generateCyber(messages, { temperature = 0.25 } = {}) {
  // Clarification / analysis path: cyber-specialized local model.
  try {
    return await ollamaChat(messages, { temperature, model: configuredCyberModel() });
  } catch {
    const cloud = await cloudChat(messages, { temperature });
    if (cloud) return cloud;
    throw new Error("Cyber model unavailable");
  }
}

function extractiveSummary(articles) {
  if (!articles.length) {
    return {
      text: "No fresh items matched the state-cyber watchlist. Refresh after feeds update.",
      model: null,
      provider: "none",
    };
  }
  const focused = articles.filter((a) => a.actors.some((x) => x !== "general"));
  const corpus = (focused.length ? focused : articles).slice(0, 18);
  const byActor = {};
  for (const a of corpus) {
    const key = a.primaryActor;
    byActor[key] = byActor[key] || [];
    byActor[key].push(a);
  }
  const movers = ["russia", "china", "northKorea", "adversarialAI", "digitalSovereignty"]
    .map((id) => {
      const items = byActor[id];
      if (!items?.length) return null;
      return `${actorLabel(id)}: ${items
        .slice(0, 2)
        .map((i) => i.title)
        .join("; ")}`;
    })
    .filter(Boolean);

  const parts = [];
  parts.push(
    movers.length
      ? `What moved: ${movers.join(" | ")}`
      : `Landscape pulse: ${corpus
          .slice(0, 3)
          .map((a) => a.title)
          .join(" · ")}.`
  );

  const sources = [...new Set(corpus.slice(0, 10).map((a) => a.sourceName))].join(", ");
  parts.push(
    `Drawn from ${articles.length} items across ${sources}. Start Ollama (model ${configuredModel()}) to restore the AI brief.`
  );
  return { text: parts.join("\n\n"), model: null, provider: "extractive" };
}

async function summarize(articles) {
  const focused = articles.filter((a) => a.actors.some((x) => x !== "general"));
  const corpus = focused.length ? focused : articles;
  if (!corpus.length) return extractiveSummary(articles);

  try {
    const result = await generate(
      [
        {
          role: "system",
          content:
            "You write short cyber threat briefs. Plain prose only. No markdown, no bullets, no headers, no recommendations section. Exactly 3 short paragraphs: (1) what moved, (2) actor implications, (3) what to watch. Cite source brands like The Record or Lawfare inline. Stay concrete.",
        },
        {
          role: "user",
          content: `Write today's executive brief from this watchlist:\n${briefBullets(corpus)}`,
        },
      ],
      { temperature: 0.2 }
    );
    return { text: result.text, model: result.model, provider: result.provider };
  } catch {
    return extractiveSummary(articles);
  }
}

async function articleBeat(article) {
  try {
    const result = await generate(
      [
        {
          role: "system",
          content:
            "Distill cyber threat journalism into one crisp beat line. Max 28 words. No preamble.",
        },
        {
          role: "user",
          content: `Title: ${article.title}\nSource: ${article.sourceName}\nLede: ${article.summary}`,
        },
      ],
      { temperature: 0.2 }
    );
    return result.text;
  } catch {
    return shorten(article.summary || article.title, 180);
  }
}

async function articleSummary(article) {
  try {
    const result = await generate(
      [
        {
          role: "system",
          content:
            "You write high-level article summaries for a cyber threat desk. Plain prose only. No markdown, no bullets, no headers. Exactly 2 short paragraphs: (1) what the piece says happened, (2) why it matters for state cyber / adversarial AI / digital sovereignty watchers. Cite the source brand once. Stay faithful to the provided lede—do not invent facts.",
        },
        {
          role: "user",
          content: `Summarize this article at a high level.\nTitle: ${article.title}\nSource: ${article.sourceName}\nPublished: ${article.publishedAt || "unknown"}\nActors: ${(article.actors || []).join(", ")}\nLede: ${article.summary || article.title}`,
        },
      ],
      { temperature: 0.2 }
    );
    return { text: result.text, model: result.model, provider: result.provider };
  } catch {
    const lede = article.summary || article.title;
    return {
      text: `${lede}\n\nHigh-level read from ${article.sourceName}. Open the original for full detail; local summarizer was unavailable.`,
      model: null,
      provider: "extractive",
    };
  }
}

async function articleClarify(article, question, summaryText = "") {
  const q = String(question || "").trim();
  if (!q) {
    return { text: "Ask a short clarification question about this article.", model: null, provider: "none" };
  }
  if (!article || !article.title) {
    return { text: "No article selected.", model: null, provider: "none" };
  }

  try {
    const result = await generateCyber(
      [
        {
          role: "system",
          content:
            "You are a cyber threat intelligence analyst for a state-sponsored cyber briefing desk covering Russia, China, North Korea, adversarial AI, and digital sovereignty. Answer the user's clarification question using the article context. Plain prose preferred; short bullets only if essential. Be concrete about actors, TTPs, and implications. Do not invent facts not supported by the context; say when something is uncertain or outside the provided material. Keep answers under ~180 words unless the question needs more.",
        },
        {
          role: "user",
          content: `Title: ${article.title}
Source: ${article.sourceName}
Published: ${article.publishedAt || "unknown"}
Actors: ${(article.actors || []).join(", ") || "unspecified"}
Lede: ${article.summary || article.title}
High-level summary: ${summaryText || "(not yet generated)"}

Clarification question: ${q}`,
        },
      ],
      { temperature: 0.25 }
    );
    return { text: result.text, model: result.model, provider: result.provider };
  } catch (err) {
    return {
      text: err?.message || "Cyber clarification model unavailable. Ensure Ollama is running with DeepHat/DeepHat-V1-7B.",
      model: null,
      provider: "error",
    };
  }
}

module.exports = {
  summarize,
  articleBeat,
  articleSummary,
  articleClarify,
  DEFAULT_MODEL,
  CYBER_MODEL,
  configuredModel,
  configuredCyberModel,
};
