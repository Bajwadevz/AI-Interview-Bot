import { useState } from 'react'
import { AuthenticationDetails, CognitoUser } from 'amazon-cognito-identity-js'
import { userPool } from '../lib/cognitoClient'
import Nav from '../components/Nav'
import Router from 'next/router'
import { saveIdToken } from '../utils/auth'

export default function Login() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [message, setMessage] = useState('')

    const handleLogin = (e) => {
        e.preventDefault()
        setMessage('Signing in...')
        const authDetails = new AuthenticationDetails({ Username: email, Password: password })
        const user = new CognitoUser({ Username: email, Pool: userPool })
        user.authenticateUser(authDetails, {
            onSuccess: (session) => {
            const idToken = session.getIdToken().getJwtToken()
            saveIdToken(idToken)
            const payload = JSON.parse(atob(idToken.split('.')[1]))
            const role = payload['custom:role'] || 'candidate'
            Router.push(`/dashboard?role=${role}`)
            },
        onFailure: (err) => {
            setMessage(err.message || JSON.stringify(err))
        }
        })
    }

    return (
        <div className="container">
            <Nav />
            <h2>Sign in</h2>
            <form onSubmit={handleLogin}>
                <label>Email</label>
                <input value={email} onChange={(e)=>setEmail(e.target.value)} type="email" required />
                <label>Password</label>
                <input value={password} onChange={(e)=>setPassword(e.target.value)} type="password" required />
                <button type="submit">Login</button>
            </form>
            <p style={{ marginTop: 12 }}>{message}</p>
            <p><a href="/forgot-password">Forgot password?</a></p>
        </div>
    )
}
