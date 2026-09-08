const { XMLParser } = (() => {
  try {
    return { XMLParser: require("fast-xml-parser").XMLParser };
  } catch {
    return { XMLParser: null };
  }
})();

const SOURCES = {
  theRecord: {
    id: "theRecord",
    name: "The Record",
    brand: "TR",
    url: "https://therecord.media/feed",
  },
  lawfare: {
    id: "lawfare",
    name: "Lawfare",
    brand: "LF",
    url: "https://www.lawfaremedia.org/feed",
  },
  krebs: {
    id: "krebs",
    name: "Krebs on Security",
    brand: "KS",
    url: "https://krebsonsecurity.com/feed/",
  },
  googleLawfare: {
    id: "googleLawfare",
    name: "Lawfare via Google News",
    brand: "LF",
    url: "https://news.google.com/rss/search?q=site:lawfaremedia.org+(cyber+OR+russia+OR+china+OR+%22north+korea%22+OR+AI+OR+sovereignty)&hl=en-US&gl=US&ceid=US:en",
  },
  googleStateCyber: {
    id: "googleStateCyber",
    name: "State cyber watch",
    brand: "GN",
    url: "https://news.google.com/rss/search?q=(Russia+OR+China+OR+%22North+Korea%22)+(cyber+OR+APT+OR+espionage)+OR+%22digital+sovereignty%22+OR+%22adversarial+AI%22&hl=en-US&gl=US&ceid=US:en",
  },
};

const UA =
  "CyberActivity/1.0 (Macintosh; Intel Mac OS X) AppleSyndication/1.0";

function stripHtml(raw = "") {
  return String(raw)
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, " ")
    .trim();
}

function classify(title, summary, categories = []) {
  const blob = [title, summary, ...categories].join(" ").toLowerCase();
  const actors = [];
  const rules = [
    ["russia", ["russia", "russian", "moscow", "kremlin", "apt28", "apt29", "fancy bear", "cozy bear", "sandworm", "gru"]],
    ["china", ["china", "chinese", "beijing", "pla", "mss", "apt41", "volt typhoon", "salt typhoon", "hafnium"]],
    ["northKorea", ["north korea", "dprk", "pyongyang", "lazarus", "andariel", "kimsuky"]],
    ["adversarialAI", ["adversarial ai", "generative ai", "llm", "deepfake", "model theft", "ai-enabled"]],
    ["digitalSovereignty", ["digital sovereignty", "data localization", "splinternet", "cyber sovereignty", "tech decoupling"]],
  ];
  for (const [id, keys] of rules) {
    if (keys.some((k) => blob.includes(k))) actors.push(id);
  }
  if (!actors.length) {
    const cyber = ["cyber", "apt", "espionage", "malware", "ransomware", "hack", "breach", "nation-state"];
    if (cyber.some((k) => blob.includes(k))) actors.push("general");
    else actors.push("general");
  }
  return actors;
}

function parseDate(raw) {
  if (!raw) return new Date().toISOString();
  const d = new Date(raw);
  return Number.isNaN(d.getTime()) ? new Date().toISOString() : d.toISOString();
}

function asArray(value) {
  if (!value) return [];
  return Array.isArray(value) ? value : [value];
}

function parseRss(xml, source) {
  // Lightweight regex fallback when fast-xml-parser isn't installed yet
  if (!XMLParser) {
    const items = [];
    const blocks = xml.split(/<item[\s>]/i).slice(1);
    for (const block of blocks.slice(0, 40)) {
      const title = stripHtml((block.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [])[1] || "");
      const link = stripHtml((block.match(/<link[^>]*>([\s\S]*?)<\/link>/i) || [])[1] || "");
      const summary = stripHtml(
        (block.match(/<description[^>]*>([\s\S]*?)<\/description>/i) || [])[1] || ""
      );
      const pubDate = (block.match(/<pubDate[^>]*>([\s\S]*?)<\/pubDate>/i) || [])[1] || "";
      const guid = stripHtml((block.match(/<guid[^>]*>([\s\S]*?)<\/guid>/i) || [])[1] || link);
      const cats = [...block.matchAll(/<category[^>]*>([\s\S]*?)<\/category>/gi)].map((m) =>
        stripHtml(m[1])
      );
      if (!title || !link) continue;
      items.push(normalizeItem({ title, link, summary, pubDate, guid, categories: cats }, source));
    }
    return items;
  }

  const parser = new XMLParser({
    ignoreAttributes: false,
    attributeNamePrefix: "@_",
    trimValues: true,
  });
  const doc = parser.parse(xml);
  const channel = doc?.rss?.channel || doc?.feed;
  const rawItems = asArray(channel?.item || channel?.entry);
  return rawItems
    .map((item) => {
      const title = stripHtml(item.title?.["#text"] || item.title || "");
      let link = "";
      if (typeof item.link === "string") link = item.link;
      else if (item.link?.["@_href"]) link = item.link["@_href"];
      else if (Array.isArray(item.link)) link = item.link[0]?.["@_href"] || item.link[0] || "";
      const summary = stripHtml(
        item.description || item.summary || item["content:encoded"] || item.content || ""
      );
      const pubDate = item.pubDate || item.published || item.updated || "";
      const guid = String(item.guid?.["#text"] || item.guid || item.id || link);
      const categories = asArray(item.category).map((c) =>
        stripHtml(typeof c === "string" ? c : c?.["#text"] || c?.["@_term"] || "")
      );
      const enclosure =
        item.enclosure?.["@_url"] || item["media:content"]?.["@_url"] || null;
      return normalizeItem(
        { title, link, summary, pubDate, guid, categories, enclosure },
        source
      );
    })
    .filter(Boolean);
}

function normalizeItem(raw, source) {
  if (!raw.title || !raw.link) return null;
  let mapped = source;
  const blob = `${raw.title} ${raw.link}`.toLowerCase();
  if (blob.includes("lawfare")) mapped = SOURCES.lawfare;
  else if (blob.includes("therecord.media")) mapped = SOURCES.theRecord;
  else if (blob.includes("krebsonsecurity")) mapped = SOURCES.krebs;

  const actors = classify(raw.title, raw.summary, raw.categories);
  return {
    id: raw.guid || raw.link,
    title: raw.title,
    summary: raw.summary,
    url: raw.link,
    publishedAt: parseDate(raw.pubDate),
    sourceId: mapped.id,
    sourceName: mapped.name,
    brand: mapped.brand,
    actors,
    primaryActor: actors.find((a) => a !== "general") || "general",
    categories: raw.categories || [],
    imageURL: raw.enclosure || null,
  };
}

async function fetchSource(source) {
  try {
    const res = await fetch(source.url, {
      headers: {
        "User-Agent": UA,
        Accept: "application/rss+xml, application/xml, text/xml, */*",
      },
    });
    if (!res.ok) return [];
    const text = await res.text();
    if (text.includes("Attention Required") || text.includes("cf-error-details")) return [];
    return parseRss(text, source);
  } catch {
    return [];
  }
}

async function fetchAllFeeds(enabledIds) {
  const ids =
    Array.isArray(enabledIds) && enabledIds.length
      ? enabledIds
      : Object.keys(SOURCES);
  const sources = ids.map((id) => SOURCES[id]).filter(Boolean);
  const batches = await Promise.all(sources.map(fetchSource));
  const merged = batches.flat();
  const seen = new Set();
  const deduped = [];
  for (const article of merged) {
    const key = article.title.toLowerCase().replace(/\s+/g, " ");
    if (seen.has(key)) continue;
    seen.add(key);
    deduped.push(article);
  }
  deduped.sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt));
  return deduped;
}

module.exports = { fetchAllFeeds, SOURCES };
