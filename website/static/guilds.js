import { get_element } from "./utils.js"
import { bot_servers } from "./config.js"
import { token } from "./auth.js"
import * as Types from "./types.js"

/**
 * @param { string } access_token authorization token/type for discord's api
 * @returns { Types.guild[] } a list of guilds that the token's user is a part of
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

/**
 * @param { Types.guild } guild the guild to make a bar for
 * @returns { HTMLDivElement } the bar it made
 */
function make_server_bar(guild)
{
    // Server icon (defaults to random ms paint image)
    let img = document.createElement("img")
    img.classList.add("server-icon")
    if (guild.icon)
        img.src = `https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png`
    else
        img.src = "/static/default_server_icon.png"
    
    // Server name
    let txt = document.createElement("div")
    txt.textContent = guild.name

    // Put it all together
    let display = document.createElement("div")
    display.classList.add("server")
    display.appendChild(img)
    display.appendChild(txt)
    display.onclick = ev => location.href = `/console/${guild.id}`
    return display
}

if (token)
{
    // Get all guilds the user is in
    let guilds = await all_guilds(token)

    // Select guilds where user has "Manage Server" perms
    // 0x28 because 0x20 is manage server and 0x08 is admin
    let settable_guilds = guilds.filter(
        g=>((parseInt(g.permissions) & 0x28) != 0) && bot_servers.some(b_g=>b_g.id == g.id)
    )

    let serverlist = get_element(["#serverlist"])
    settable_guilds.forEach(guild => {
        serverlist.appendChild(make_server_bar(guild))
    });
    console.log(settable_guilds.map(g=>g.name))
}