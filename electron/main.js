const { app, BrowserWindow, dialog, ipcMain, session, shell } = require("electron");
const { spawn } = require("child_process");
const http = require("http");
const path = require("path");

const PROJECT_ROOT = path.join(__dirname, "..");
const PORT = process.env.JARVIS_PORT || 8000;
const APP_URL = `http://127.0.0.1:${PORT}`;
const HEALTH_URL = `${APP_URL}/healthz`;

let backendProcess = null;
let mainWindow = null;

function spawnBackend() {
  const pythonCmd = process.platform === "win32" ? "python" : "python3";
  backendProcess = spawn(
    pythonCmd,
    ["-m", "uvicorn", "backend.app:app", "--port", String(PORT)],
    { cwd: PROJECT_ROOT, stdio: "pipe" }
  );

  backendProcess.stdout.on("data", (data) => console.log(`[backend] ${data}`));
  backendProcess.stderr.on("data", (data) => console.error(`[backend] ${data}`));
  backendProcess.on("error", (err) => {
    console.error("Failed to start backend:", err);
    showBackendErrorDialog(err.message);
  });
}

function waitForBackend(retries = 30, delayMs = 500) {
  return new Promise((resolve, reject) => {
    const attempt = (remaining) => {
      const request = http.get(HEALTH_URL, (res) => {
        if (res.statusCode === 200) {
          resolve();
        } else if (remaining > 0) {
          setTimeout(() => attempt(remaining - 1), delayMs);
        } else {
          reject(new Error("Backend wurde nicht rechtzeitig bereit."));
        }
      });
      request.on("error", () => {
        if (remaining > 0) {
          setTimeout(() => attempt(remaining - 1), delayMs);
        } else {
          reject(new Error("Backend wurde nicht rechtzeitig bereit."));
        }
      });
    };
    attempt(retries);
  });
}

function showBackendErrorDialog(message) {
  dialog.showErrorBox(
    "Jarvis-Backend konnte nicht gestartet werden",
    "Stelle sicher, dass Python 3 und die Backend-Abhängigkeiten installiert sind " +
      `(pip install -r backend/requirements.txt).\n\nFehler: ${message}`
  );
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 860,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(__dirname, "preload.js"),
    },
  });
  mainWindow.loadURL(APP_URL);
  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

function killBackend() {
  if (backendProcess && !backendProcess.killed) {
    backendProcess.kill();
    backendProcess = null;
  }
}

app.whenReady().then(async () => {
  session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
    const url = webContents.getURL();
    callback(permission === "media" && url.startsWith(APP_URL));
  });

  spawnBackend();
  try {
    await waitForBackend();
    createWindow();
  } catch (err) {
    showBackendErrorDialog(err.message);
    app.quit();
    return;
  }

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("before-quit", killBackend);
app.on("will-quit", killBackend);

ipcMain.handle("open-external", (_event, url) => {
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
      return { ok: false, error: "Unsupported URL scheme" };
    }
    shell.openExternal(url);
    return { ok: true };
  } catch {
    return { ok: false, error: "Invalid URL" };
  }
});

ipcMain.handle("get-version", () => app.getVersion());
