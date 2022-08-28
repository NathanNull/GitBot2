/**
 * @type {import("./guilds").guild[]}
 */
let bot_servers = await fetch(`http://${location.hostname}:3001/botservers`)
    .then(result => result.json())

export { bot_servers }