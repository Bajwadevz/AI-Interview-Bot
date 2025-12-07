import Nav from '../components/Nav'
import ProtectedRoute from '../components/ProtectedRoute'
import { getIdToken, decodeJwt } from '../utils/auth'
import { useEffect, useState } from 'react'

export default function Dashboard() {
    const [profile, setProfile] = useState(null)

    useEffect(() => {
        const token = getIdToken()
        const payload = token ? decodeJwt(token) : null
        setProfile(payload)
    }, [])

    return (
    <ProtectedRoute>
        <div className="container">
            <Nav />
            <h2>Dashboard</h2>
            {profile ? (
            <>
                <p>Welcome, <strong>{profile.name || profile.email}</strong></p>
                <p>Role: <strong>{profile['custom:role']}</strong></p>
                <p>sub: <code>{profile.sub}</code></p>
            </>
            ) : (
            <p>Loading profile...</p>
            )}
        </div>
        </ProtectedRoute>
    )
}
