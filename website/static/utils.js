/**
 *   @param { string[] } selectors element chain from body to element
 *   @return { HTMLElement } selected element
 */
function get_element(selectors)
{
    let element = document.body
    for (let s of selectors) {
        element = element.querySelector(s)
    }
    return element
}

/**
 *   @param { ()=>boolean } is_ready test if the function should fire
 *   @param { ()=>void } when_ready function to fire when is_ready evaluates true
 */
function check_until_ready(is_ready, when_ready)
{
    if (is_ready())
        when_ready()
    else
        setTimeout(() => {
            check_until_ready(is_ready, when_ready)
        }, 1000);
}

export { get_element, check_until_ready }