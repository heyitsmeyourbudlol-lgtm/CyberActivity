const { app, BrowserWindow, ipcMain, shell, nativeTheme } = require("electron");
const path = require("path");
const { fetchAllFeeds } = require("./feeds");
const { summarize, articleBeat, articleSummary, articleClarify } = require("./summary");

nativeTheme.themeSource = "light";

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 860,
    minWidth: 1020,
    minHeight: 700,
    titleBarStyle: "hiddenInset",
    trafficLightPosition: { x: 16, y: 18 },
    backgroundColor: "#ecebe4",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  mainWindow.loadFile(path.join(__dirname, "..", "renderer", "index.html"));

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });
}

app.whenReady().then(() => {
  createWindow();
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

ipcMain.handle("briefing:refresh", async (_event, enabledSources) => {
  const articles = await fetchAllFeeds(enabledSources);
  const summary = await summarize(articles);
  const beats = {};
  // Beat lines for the first few posters; keep this bounded so refresh stays snappy.
  for (const article of articles.slice(0, 8)) {
    beats[article.id] = await articleBeat(article);
  }
  return {
    articles,
    executiveSummary: summary.text,
    summaryModel: summary.model,
    summaryProvider: summary.provider,
    beats,
    refreshedAt: new Date().toISOString(),
  };
});

ipcMain.handle("shell:open", async (_event, url) => {
  await shell.openExternal(url);
});

ipcMain.handle("article:summarize", async (_event, article) => {
  if (!article || !article.title) {
    return { text: "No article selected.", model: null, provider: "none" };
  }
  return articleSummary(article);
});

ipcMain.handle("article:clarify", async (_event, payload) => {
  const article = payload?.article;
  const question = payload?.question;
  const summaryText = payload?.summaryText || "";
  if (!article || !article.title) {
    return { text: "No article selected.", model: null, provider: "none" };
  }
  return articleClarify(article, question, summaryText);
});
