import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import Signup from '../pages/signup'
import * as cognito from '../lib/cognitoClient'

describe('Signup Page', () => {
    test('displays success message after mock signup', async () => {
        const mockSignUp = jest.fn((email, pass, attrs, data, cb) => {
            cb(null, { user: { username: email } })
        })
        cognito.userPool = { signUp: mockSignUp }

        render(<Signup />)
        fireEvent.change(screen.getByPlaceholderText('Ali H. Mughal'), { target: { value: 'Ali' } })
        fireEvent.change(screen.getByPlaceholderText('you@example.com'), { target: { value: 'ali@example.com' } })
        fireEvent.change(screen.getByPlaceholderText('Strong password'), { target: { value: 'pass1234' } })
        fireEvent.click(screen.getByText('Sign up'))

        await waitFor(() =>
            expect(screen.getByText(/Signup successful/i)).toBeInTheDocument()
        )
        expect(mockSignUp).toHaveBeenCalled()
    })

    test('shows error message on Cognito failure', async () => {
        const mockSignUp = jest.fn((a, b, c, d, cb) => cb(new Error('Cognito failed'), null))
        cognito.userPool = { signUp: mockSignUp }

        render(<Signup />)
        fireEvent.change(screen.getByPlaceholderText('Ali H. Mughal'), { target: { value: 'Ali' } })
        fireEvent.change(screen.getByPlaceholderText('you@example.com'), { target: { value: 'ali@example.com' } })
        fireEvent.change(screen.getByPlaceholderText('Strong password'), { target: { value: 'pass1234' } })
        fireEvent.click(screen.getByText('Sign up'))

        await waitFor(() =>
            expect(screen.getByText(/Cognito failed/i)).toBeInTheDocument()
        )
    })
})
