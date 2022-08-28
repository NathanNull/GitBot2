import { get_element } from "./utils.js"
import { bot_servers } from "./config.js"
import { token } from "./auth.js"

/**
 * @typedef {{id: string, name: string, permissions: string}} guild
 */

/**
 * @typedef
 * @param { string } access_token authorization token/type for discord's api
 * @returns { guild[] } a list of guilds that the token's user is a part of
 */
async function all_guilds(access_token)
{
    let result = await fetch("https://discord.com/api/users/@me/guilds", {
        headers: {
            authorization: access_token
        },
    }).then(result=>result.json())
    return result
}

if (token)
{
    // Get all guilds the user is in
    let guilds = await all_guilds(token)

    // Select guilds where user has "Manage Server" perms
    let settable_guilds = guilds.filter(
        g=>((parseInt(g.permissions) & 0x28) != 0) && bot_servers.some(b_g=>b_g.id == g.id)
    )

    let content = get_element(["#content"])
    let serverlist = document.createElement("div")
    serverlist.id = "serverlist"
    content.appendChild(serverlist)

    settable_guilds.forEach(guild => {
        let display = document.createElement("div")
        display.textContent = guild.name
        content.appendChild(display)
    });
    console.log(settable_guilds.map(g=>g.name))
}