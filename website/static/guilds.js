import { check_until_ready } from "./utils.js"
import { bot_auth } from "./config.js"

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

async function get_guilds()
{
    // Get all guilds the user is in
    let auth = sessionStorage.getItem("discord_token")
    let guilds = await all_guilds(auth)

    // Get bot guild names
    let bot_guilds = await all_guilds(bot_auth)

    // Select guilds where user has "Manage Server" perms
    let settable_guilds = guilds.filter(
        g=>((parseInt(g.permissions) & 0x28) != 0) && bot_guilds.some(b_g=>b_g.id == g.id)
    )

    settable_guilds.forEach(guild => {
        
    });
    console.log(settable_guilds.map(g=>g.name))
}

check_until_ready(()=>"discord_token" in sessionStorage, get_guilds)