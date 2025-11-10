import { saveIdToken, getIdToken, clearTokens, decodeJwt } from '../utils/auth'

describe('Auth Utils', () => {
    beforeEach(() => localStorage.clear())

    test('saveIdToken and getIdToken should store and retrieve the token', () => {
        saveIdToken('dummy-token')
        expect(getIdToken()).toBe('dummy-token')
    })

    test('clearTokens should remove token from localStorage', () => {
        saveIdToken('dummy-token')
        clearTokens()
        expect(getIdToken()).toBeNull()
    })

    test('decodeJwt should correctly decode a simple JWT', () => {
        // header.payload.signature -> payload base64 = {"user":"ali"}
        const payload = btoa(JSON.stringify({ user: 'ali' }))
        const token = `aaa.${payload}.bbb`
        expect(decodeJwt(token)).toEqual({ user: 'ali' })
    })

    test('decodeJwt should return null for invalid tokens', () => {
        expect(decodeJwt('not-a-jwt')).toBeNull()
    })
})
