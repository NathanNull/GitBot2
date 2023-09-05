import { get_element } from "./utils.js"
import { userdata } from "./auth.js"

if (userdata)
{
    let uname = userdata.username
    let avatar_url = `https://cdn.discordapp.com/avatars/${userdata.id}/a_${userdata.avatar}.png?size=128`

    // Show logged-in elements
    get_element(["#user-details"]).style.display = "flex"
    get_element(["#info"]).textContent = uname
    let pfp_elem = get_element(["#pfp"])
    pfp_elem.src = avatar_url
    pfp_elem.style.display = "block"

    // Change logo link to serverlist
    let logo = get_element(["#logo"])
    logo.href = "/serverlist"
}

