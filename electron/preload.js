const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("cyberactivity", {
  refresh: (enabledSources) => ipcRenderer.invoke("briefing:refresh", enabledSources),
  openExternal: (url) => ipcRenderer.invoke("shell:open", url),
  summarizeArticle: (article) => ipcRenderer.invoke("article:summarize", article),
  clarifyArticle: (payload) => ipcRenderer.invoke("article:clarify", payload),
});
