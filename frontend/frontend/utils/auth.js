export function saveIdToken(token) {
    if (typeof window !== 'undefined') {
        localStorage.setItem('idToken', token)
    }
}

export function getIdToken() {
    if (typeof window === 'undefined') return null
    return localStorage.getItem('idToken')
}

export function clearTokens() {
    if (typeof window !== 'undefined') localStorage.removeItem('idToken')
}

export function decodeJwt(token) {
    try {
        const payload = token.split('.')[1]
        return JSON.parse(atob(payload))
    } catch (err) {
        return null
    }
}
