import { useEffect, useState } from 'react'
import Router from 'next/router'
import { getIdToken, decodeJwt } from '../utils/auth'

export default function ProtectedRoute({ children, roles = [] }) {
    const [checking, setChecking] = useState(true)

    useEffect(() => {
        const token = getIdToken()
        if (!token) {
            Router.replace('/login')
            return
        }
        const payload = decodeJwt(token)
        if (!payload) {
            Router.replace('/login')
            return
        }
        if (roles.length && !roles.includes(payload['custom:role'])) {
            Router.replace('/login')
            return
        }
        setChecking(false)
    }, [])

    if (checking) return <div className="container">Loading...</div>
    return <>{children}</>
}
