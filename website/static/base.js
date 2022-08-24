main = () => {
    // Get URL params manually, since nothing else seems to work properly
    let params = {}
    new URLSearchParams(window.location.hash.slice(1))
        .forEach((val, key) => {
            params[key] = val
        })
    let { access_token, token_type } = params

    if (!access_token && "discord_token" in sessionStorage) // Check if it's stored in sessionStorage, if so then use it.
        [ token_type, access_token ] = sessionStorage.getItem("discord_token").split(" ")

    if (!access_token) // If it isn't, then let the user log in.
    {
        document.addEventListener("DOMContentLoaded",
            ()=>document.getElementById("login").style.display = "inline-block"
        )
        return
    }

    console.log("has token from somewhere")

    fetch("https://discord.com/api/users/@me", {
        headers: {
            "Authorization": `${token_type} ${access_token}`
        },
    }).then(result=>result.json()).then(json=>{
        let uname = json.username
        let disc = json.discriminator
        let avatar_url = `https://cdn.discordapp.com/avatars/${json.id}/a_${json.avatar}.png?size=32`
        window.sessionStorage.setItem("discord_user_data", JSON.stringify(json))
        document.getElementById("info").textContent = `${uname}#${disc}`
        console.log(avatar_url)
        document.getElementById("pfp").src = avatar_url
        document.getElementById("pfp").style.display = "block"
    })
    window.sessionStorage.setItem("discord_token", `${token_type} ${access_token}`)
}

main()