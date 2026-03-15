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
        link + ' <button onclick="copyLink(\'' + link + '\')">copy</button>'
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
    } else {
        document.getElementById('auth-result').innerText = 'user exists'
    }
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
    } else {
        document.getElementById('auth-result').innerText = 'wrong login or password'
    }
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
        link + ' <button onclick="copyLink(\'' + link + '\')">copy</button>'
}


async function search() {

    const url = document.getElementById('search-url').value

    const r = await fetch('/links/search?original_url=' + encodeURIComponent(url))

    if (!r.ok) {
        document.getElementById('search-result').innerText = 'not found'
        return
    }

    const data = await r.json()

    const link = window.location.origin + '/' + data.short_code

    document.getElementById('search-result').innerHTML =
        link + ' <button onclick="copyLink(\'' + link + '\')">copy</button>'
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