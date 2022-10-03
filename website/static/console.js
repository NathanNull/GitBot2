import { get_element } from "./utils.js"
import { bot_servers } from "./config.js"

let config_names = ["music", "level", "moderation", "reaction_roles"]

async function enable_disable()
{
    let config_states = config_names.map(name => [name, get_element(["#"+name]).checked]);
    await notify_bot("config", Object.fromEntries(config_states))
}
get_element(["#config-apply"]).onclick = enable_disable

async function audit_channel()
{
    let selected = get_element(["#audit-channel"]).value
    if (selected == "-default")
    {
        console.log("default")
        return
    }
    await notify_bot("auditchannel", selected)
}
get_element(["#audit-apply"]).onclick = audit_channel

function make_word(word)
{
    let ele = document.createElement("li")
    let rm = document.createElement("button")
    rm.textContent = "Remove"
    rm.onclick = ()=>{
        ele.remove()
        update_banned_words()
    }
    let txt = document.createElement("div")
    txt.textContent = word
    txt.style.display = "inline"
    ele.appendChild(rm)
    ele.appendChild(txt)
    get_element(["#bannedwords"]).appendChild(ele)
}

async function update_banned_words()
{
    let newword = get_element(["#banword-input"]).value
    let all_words = Array.from(get_element(["#bannedwords"]).childNodes.values()).map(e=>e.lastChild.textContent)
    if (newword !== "")
    {
        all_words.push(newword)
        get_element(["#banword-input"]).value = ""
        make_word(newword)
    }
    await notify_bot("bannedwords", all_words)
}
get_element(["#banword-confirm"]).onclick = update_banned_words
get_element(["#banword-input"]).addEventListener("keydown", ev=>{
    if (ev.key === "Enter") update_banned_words()
})

async function notify_bot(type, info)
{
    let data = {type,gid:serverid,info}
    let url = `http://${location.hostname}:3001/notify-bot`
    let res = await fetch(url, {
        headers: {
            'Content-Type': 'application/json'
        },
        method: "POST",
        body: JSON.stringify(data)
    })
    console.log(await res.text())
}

async function main()
{
    let base_url = `http://${location.hostname}:3001/bot-info/${serverid}`
    let this_guild = bot_servers.find(g => g.id==serverid)

    let config = await (await fetch(base_url+"/config")).json()
    config_names.forEach(name => {
        let element = get_element(["#"+name])
        element.checked = config[name]
    });

    let all_channels = await fetch(`http://${location.hostname}:3001/channels/${this_guild.id}`).then(r=>r.json())
    all_channels = all_channels.filter(c=>c.type==0) //0 for GUILD_TEXT
    let audit_select = get_element(["#audit-channel"])
    all_channels.forEach(channel => {
        let opt = document.createElement("option")
        opt.value = channel.id
        opt.textContent = channel.name
        audit_select.appendChild(opt)
    })

    let banned_words = await fetch(base_url+"/bannedwords").then(r=>r.json())
    banned_words.forEach(w => {
        make_word(w)
    })
}
await main()