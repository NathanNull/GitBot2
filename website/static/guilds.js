function check_until_ready(is_ready, when_ready)
{
    if (is_ready())
        when_ready()
    else
        setTimeout(() => {
            check_until_ready(is_ready, when_ready)
        }, 1000);
}

let token = null

function get_guilds()
{
    console.log("hey it's me")
    authorization = window.sessionStorage.getItem("discord_token")
    console.log(authorization)
    fetch("https://discord.com/api/users/@me/guilds", {
        headers: {
            authorization
        },
    }).then(result=>result.json()).then(json=>{
        const perm_id = 0x20
        let managed_guilds = []
        json.forEach(partial=>
        {
            if ((parseInt(partial.permissions) & perm_id) != 0)
                managed_guilds.push(partial)
        })
        console.log(managed_guilds.map(g=>g.name))
    })
}

check_until_ready(()=>"discord_token" in window.sessionStorage, get_guilds)