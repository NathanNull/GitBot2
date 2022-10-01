console.log(serverid)

async function notify_bot()
{
    data = JSON.stringify({test: 1212})
    let url = `http://${location.hostname}:3001/notify-bot/${data}`
    let res = await fetch(url)
    console.log(await res.text())
}