import { useState } from 'react'
import { CognitoUser } from 'amazon-cognito-identity-js'
import { userPool } from '../lib/cognitoClient'
import Nav from '../components/Nav'

export default function ForgotPassword() {
    const [email, setEmail] = useState('')
    const [stage, setStage] = useState('request') // request or confirm
    const [code, setCode] = useState('')
    const [newPassword, setNewPassword] = useState('')
    const [message, setMessage] = useState('')

    const requestReset = async (e) => {
        e.preventDefault()
        setMessage('Requesting reset code...')
        const user = new CognitoUser({ Username: email, Pool: userPool })
        user.forgotPassword({
            onSuccess: () => setMessage('Password reset success — you can now login'),
            onFailure: (err) => setMessage(err.message || JSON.stringify(err)),
            inputVerificationCode: (data) => setStage('confirm')
        })
    }

    const confirmReset = async (e) => {
        e.preventDefault()
        setMessage('Confirming new password...')
        const user = new CognitoUser({ Username: email, Pool: userPool })
        user.confirmPassword(code, newPassword, {
            onSuccess: () => setMessage('Password reset complete — please login'),
            onFailure: (err) => setMessage(err.message || JSON.stringify(err))
        })
    }

    return (
    <div className="container">
        <Nav />
        <h2>Forgot password</h2>

        {stage === 'request' ? (
            <form onSubmit={requestReset}>
                <label>Enter your email</label>
                <input value={email} onChange={(e)=>setEmail(e.target.value)} type="email" required />
                <button type="submit">Send reset code</button>
            </form>
        ) : (
            <form onSubmit={confirmReset}>
                <label>Confirmation code</label>
                <input value={code} onChange={(e)=>setCode(e.target.value)} required />
                <label>New password</label>
                <input value={newPassword} onChange={(e)=>setNewPassword(e.target.value)} type="password" required />
                <button type="submit">Confirm new password</button>
            </form>
        )}

        <p style={{ marginTop: 12 }}>{message}</p>
    </div>
    )
}
