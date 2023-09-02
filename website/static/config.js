import * as Types from "./types.js"

/**
 * @type {Types.guild[]}
 */
let bot_servers = await fetch(`http://${location.host}/api/botservers`)
    .then(result => result.json())

export { bot_servers }