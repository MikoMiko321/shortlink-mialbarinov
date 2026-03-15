async function shorten() {

    const url = document.getElementById('url').value
    if (!url) return

    const r = await fetch('/links/shorten', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({original_url: url})
    })

    const data = await r.json()

    const link = window.location.origin + '/' + data.short_code

    document.getElementById('short-result').innerHTML =
        '<div>' +
        link +
        ' <button onclick="copyLink(\'' + link + '\')">copy</button>' +
        '</div>'
}


async function register() {

    const login = document.getElementById('login').value
    const password = document.getElementById('password').value

    const r = await fetch('/auth/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({login: login, password: password})
    })

    if (r.ok) {
        window.location = '/static/dashboard.html'
        return
    }

    const err = await r.json()

    document.getElementById('auth-result').innerText =
        JSON.stringify(err.detail)
}


async function login() {

    const login = document.getElementById('login').value
    const password = document.getElementById('password').value

    const r = await fetch('/auth/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({login: login, password: password})
    })

    if (r.ok) {
        window.location = '/static/dashboard.html'
        return
    }

    const err = await r.json()

    document.getElementById('auth-result').innerText =
        JSON.stringify(err.detail)
}


async function create() {

    const url = document.getElementById('url').value
    const alias = document.getElementById('alias').value

    const r = await fetch('/links/shorten', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            original_url: url,
            custom_alias: alias ? alias : null
        })
    })

    const data = await r.json()

    const link = window.location.origin + '/' + data.short_code

    document.getElementById('create-result').innerHTML =
        '<div>' +
        link +
        ' <button onclick="copyLink(\'' + link + '\')">copy</button>' +
        '</div>'
}


async function search() {

    const fragment = document.getElementById('search-url').value

    if (fragment.length < 4) {
        document.getElementById('search-result').innerText =
            'enter at least 4 characters'
        return
    }

    const r = await fetch('/links/search?fragment=' + encodeURIComponent(fragment))

    const data = await r.json()

    if (!data.length) {
        document.getElementById('search-result').innerText = 'not found'
        return
    }

    let html = ''

    for (const l of data) {

        const short = window.location.origin + '/' + l.short_code

        html +=
            '<div>' +
            short +
            ' <button onclick="copyLink(\'' + short + '\')">copy</button>' +
            '<br>' +
            '<small>' + l.original_url + '</small>' +
            '</div><br>'
    }

    document.getElementById('search-result').innerHTML = html
}


async function stats() {

    const code = document.getElementById('stats-code').value

    const r = await fetch('/links/' + code + '/stats')

    if (!r.ok) {
        document.getElementById('stats-result').innerText = 'not found'
        return
    }

    const data = await r.json()

    document.getElementById('stats-result').innerText =
        JSON.stringify(data, null, 2)
}


async function update() {

    const code = document.getElementById('update-code').value
    const url = document.getElementById('update-url').value

    const r = await fetch('/links/' + code, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({original_url: url})
    })

    if (!r.ok) {
        alert('not found')
    } else {
        alert('updated')
    }
}


async function remove() {

    const code = document.getElementById('delete-code').value

    const r = await fetch('/links/' + code, {
        method: 'DELETE'
    })

    if (!r.ok) {
        document.getElementById('delete-result').innerText = 'not found'
    } else {
        document.getElementById('delete-result').innerText = 'deleted'
    }
}


function copyLink(link) {
    navigator.clipboard.writeText(link)
}


async function logout() {
    await fetch('/auth/logout', {method: 'POST'})
    window.location = '/'
}