let bot_auth = await fetch(`http://${location.hostname}:3001/token`)
    .then(result => result.json())
    .then(json => `Bot ${json.token}`)

export { bot_auth }