console.log(serverid)

async function enable_disable()
{
    
}

async function notify_bot(type, info)
{
    let data = {type,gid:serverid,info}
    let url = `http://${location.hostname}:3001/notify-bot`
    let res = await fetch(url, {
        headers: {
            'Content-Type': 'application/json'
        },
        method: "POST",
        body: JSON.stringify(data)
    })
    console.log(await res.text())
}

