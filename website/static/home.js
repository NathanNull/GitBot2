import { get_element } from "./utils.js";

async function main() {
    let feedback_box = get_element(['#feedback'])
    let feedback_submit = get_element(['#feedback-submit'])
    feedback_submit.onclick = async () => {
        let data = feedback_box.value
        await fetch(`${location.protocol}//${location.host}/api/sendmsg`, {
            headers: {
                'Content-Type': 'application/json'
            },
            method: "POST",
            body: JSON.stringify(data)
        })
        feedback_box.value = ""
    }
}
await main()