import { get_element } from "./utils.js"

let token;
let userdata;

let main = async () => {
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

    await fetch("https://discord.com/api/users/@me", {
        headers: {
            "Authorization": `${token_type} ${access_token}`
        },
    }).then(result=>result.json()).then(json=>{
        // Store json
        //window.sessionStorage.setItem("discord_user_data", JSON.stringify(json))
        userdata = json
    })
    sessionStorage.setItem("discord_token", `${token_type} ${access_token}`)
    token = `${token_type} ${access_token}`
}

await main()

export { token, userdata }