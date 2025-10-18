import { useState } from 'react'
import { userPool } from '../lib/cognitoClient'
import { CognitoUserAttribute } from 'amazon-cognito-identity-js'
import Nav from '../components/Nav'
import Router from 'next/router'

export default function Signup() {
    const [email, setEmail] = useState('')
    const [name, setName] = useState('')
    const [password, setPassword] = useState('')
    const [role, setRole] = useState('candidate')
    const [message, setMessage] = useState('')

    const handleSignup = (e) => {
        e.preventDefault()
        setMessage('Creating account...')
        const attributes = [
            { Name: 'name', Value: name },
            { Name: 'custom:role', Value: role }
        ].map(a => new CognitoUserAttribute(a))

        userPool.signUp(email, password, attributes, null, (err, result) => {
        if (err) {
            setMessage(err.message || JSON.stringify(err))
            return
        }
        setMessage('Signup successful — check your email for a confirmation code.')
        // redirect to login so user can confirm (or you can create a separate confirm flow)
        setTimeout(() => Router.push('/login'), 1200)
        })
    }

    return (
        <div className="container">
            <Nav />
            <h2>Create an account</h2>
            <form onSubmit={handleSignup}>
                <label>Full name</label>
                <input value={name} onChange={(e)=>setName(e.target.value)} placeholder="Ali H. Mughal" required />
                <label>Email</label>
                <input value={email} onChange={(e)=>setEmail(e.target.value)} type="email" placeholder="you@example.com" required />
                <label>Password</label>
                <input value={password} onChange={(e)=>setPassword(e.target.value)} type="password" placeholder="Strong password" required />
                <label>Role</label>
                <select value={role} onChange={(e)=>setRole(e.target.value)}>
                    <option value="candidate">Candidate</option>
                    <option value="admin">Admin</option>
                </select>
                <button type="submit">Sign up</button>
            </form>
            <p style={{ marginTop: 12 }}>{message}</p>
        </div>
    )
}
