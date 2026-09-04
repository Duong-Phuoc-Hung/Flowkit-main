const { app, BrowserWindow } = require('electron')
const path = require('path')

let mainWindow

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    title: 'FlowKit AI Studio V14.0 Pro',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  })

  // In production, we load the Next.js server.
  // In development, wait-on ensures localhost:3000 is ready before this runs.
  mainWindow.loadURL('http://localhost:3000')

  mainWindow.on('closed', function () {
    mainWindow = null
  })
}

app.whenReady().then(() => {
  createWindow()
  
  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit()
})
