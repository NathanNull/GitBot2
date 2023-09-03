import { get_element } from "./utils.js"

let token;
let userdata;

let main = async () => {
    // Get URL fragment
    let params = new URLSearchParams(window.location.search.slice(1))
    let code = params.get("code")
    let token_type, access_token

    if (!code) {
        if ("discord_token" in sessionStorage) // Check if it's stored in sessionStorage, if so then use it.
            [token_type, access_token] = sessionStorage.getItem("discord_token").split(" ")
        else // If it isn't, then let the user log in.
        {
            document.addEventListener("DOMContentLoaded",
                () => get_element(["#login"]).style.display = "flex"
            )
            return
        }
    } else {
        if (location.host == "192.18.140.33:8080") {
            let urla = "surfbot.my.to";
            console.log(urla)
            const data = new URLSearchParams()
            let body = {
                client_id: window.client_id,
                client_secret: window.client_secret,
                grant_type: 'authorization_code',
                code,
                //redirect_uri: 'http://' + location.host + location.pathname
                redirect_uri: 'http://' + urla + location.pathname
            }
            for (let key in body) {
                console.log(encodeURI(body[key]))
                data.append(encodeURI(key), encodeURI(body[key]))
            }
            console.log(body)
            console.log(Array(...data.entries()))
            let res = await fetch("https://discord.com/api/oauth2/token", {
                method: 'POST',
                body: data,
                headers: {
                    'Content-Type': "application/x-www-form-urlencoded"
                }
            }).then(r => r.json())
            console.log(res)
            if ('access_token' in res) {
                access_token = res.access_token
                token_type = res.token_type
            } else return
        } else {
            let urla = location.host;
            console.log(urla)
            const data = new URLSearchParams()
            let body = {
                client_id: window.client_id,
                client_secret: window.client_secret,
                grant_type: 'authorization_code',
                code,
                //redirect_uri: 'http://' + location.host + location.pathname
                redirect_uri: 'http://' + urla + location.pathname
            }
            for (let key in body) {
                console.log(encodeURI(body[key]))
                data.append(encodeURI(key), encodeURI(body[key]))
            }
            console.log(body)
            console.log(Array(...data.entries()))
            let res = await fetch("https://discord.com/api/oauth2/token", {
                method: 'POST',
                body: data,
                headers: {
                    'Content-Type': "application/x-www-form-urlencoded"
                }
            }).then(r => r.json())
            console.log(res)
            if ('access_token' in res) {
                access_token = res.access_token
                token_type = res.token_type
            } else return
        }
        /*const data = new URLSearchParams()
        let body = {
            //client_id: window.client_id,
            //client_secret: window.client_secret,
            //grant_type: 'authorization_code',
            //code,
            //redirect_uri: 'http://' + location.host + location.pathname
            //redirect_uri: 'http://' + urla + location.pathname
        //}
        for (let key in body) {
            console.log(encodeURI(body[key]))
            data.append(encodeURI(key), encodeURI(body[key]))
        }
        console.log(body)
        console.log(Array(...data.entries()))
        let res = await fetch("https://discord.com/api/oauth2/token", {
            method: 'POST',
            body: data,
            headers: {
                'Content-Type': "application/x-www-form-urlencoded"
            }
        }).then(r => r.json())
        console.log(res)
        if ('access_token' in res) {
            access_token = res.access_token
            token_type = res.token_type
        } else return*/
    }

    await fetch("https://discord.com/api/users/@me", {
        headers: {
            "Authorization": `${token_type} ${access_token}`
        },
    }).then(result => result.json()).then(json => {
        // Store json
        //window.sessionStorage.setItem("discord_user_data", JSON.stringify(json))
        userdata = json
    })
    sessionStorage.setItem("discord_token", `${token_type} ${access_token}`)
    token = `${token_type} ${access_token}`
}

await main()

export { token, userdata }