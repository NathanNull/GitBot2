import { get_element } from "./utils.js"

let main = () => {
    // Get URL fragment
    let params = new URLSearchParams(window.location.hash.slice(1))
    let [ access_token, token_type ] = [ params.get("access_token"), params.get("token_type") ]

    if (!access_token)
    {
        if ("discord_token" in sessionStorage) // Check if it's stored in sessionStorage, if so then use it.
            [ token_type, access_token ] = sessionStorage.getItem("discord_token").split(" ")
        else // If it isn't, then let the user log in.
        {
            document.addEventListener("DOMContentLoaded",
                ()=>get_element(["#login"]).style.display = "flex"
            )
            return
        }
    }

    fetch("https://discord.com/api/users/@me", {
        headers: {
            "Authorization": `${token_type} ${access_token}`
        },
    }).then(result=>result.json()).then(json=>{
        // Parse JSON somewhat
        let uname = json.username
        let disc = json.discriminator
        let avatar_url = `https://cdn.discordapp.com/avatars/${json.id}/a_${json.avatar}.png?size=128`

        // Store json in session storage
        window.sessionStorage.setItem("discord_user_data", JSON.stringify(json))

        // Show logged-in elements
        get_element(["#info"]).textContent = `${uname}#${disc}`
        let pfp_elem = get_element(["#pfp"])
        pfp_elem.src = avatar_url
        pfp_elem.style.display = "block"
    })
    window.sessionStorage.setItem("discord_token", `${token_type} ${access_token}`)
}

main()