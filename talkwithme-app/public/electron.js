const {app, BrowserWindow} = require('electron');

const url = require('url');
const path = require('path');
const { title } = require('process');
const { create } = require('domain');


function createMainWindows() {
    const mainWindows = new BrowserWindow({
        title: 'Talkwithmeapp',
        width:800,
        geight:800,
    });
    const startUrl = url.format({
        pathname:path.join(__dirname,'../build/index.html'), //connect to react app from path
        protocol:'file:',
        slashes:true,
    });
    mainWindows.loadURL(startUrl)
}

app.whenReady().then(()=>{
    createMainWindows()

    app.on('activate', () =>{
        if(BrowserWindow.getAllWindows().lenght === 0)createMainWindows()
    })
});

app.on('windows-all-closed',() =>{
    if(process.platform != 'darwin'){
        app.quit()
    }
});