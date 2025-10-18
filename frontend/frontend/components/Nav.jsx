import Link from 'next/link'
import { useEffect, useState } from 'react'
import { getIdToken, decodeJwt, clearTokens } from '../utils/auth'

export default function Nav() {
    const [user, setUser] = useState(null)

    useEffect(() => {
        const token = getIdToken()
            if (token) {
                const payload = decodeJwt(token)
                setUser(payload)
            }
    }, [])

    function logout() {
        clearTokens()
        if (typeof window !== 'undefined') window.location.href = '/login'
    }

    return (
        <div style={{ marginBottom: 16 }}>
            <nav style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
                <div>
                    <Link href="/" style={{ marginRight: 12 }}>Home</Link>
                    <Link href="/signup" style={{ marginRight: 12 }}>Sign up</Link>
                    <Link href="/login" style={{ marginRight: 12 }}>Login</Link>
                </div>
                <div>
                    {user ? (
                        <>
                            <span style={{ marginRight: 12 }}>{user.email}</span>
                            <button onClick={logout}>Logout</button>
                        </>
                    ) : (
                        <Link href="/login">Sign in</Link>
                    )}
                </div>
            </nav>
        </div>
    )
}
