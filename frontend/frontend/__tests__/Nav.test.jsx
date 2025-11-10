import { render, screen, fireEvent } from '@testing-library/react'
import Nav from '../components/Nav'
import * as auth from '../utils/auth'

describe('Nav Component', () => {
    afterEach(() => jest.restoreAllMocks())

    test('renders default links when user not logged in', () => {
        jest.spyOn(auth, 'getIdToken').mockReturnValue(null)
        render(<Nav />)
        expect(screen.getByText('Home')).toBeInTheDocument()
        expect(screen.getByText('Sign up')).toBeInTheDocument()
        expect(screen.getByText('Login')).toBeInTheDocument()
    })

    test('renders email and logout when user logged in', () => {
        jest.spyOn(auth, 'getIdToken').mockReturnValue('fake')
        jest.spyOn(auth, 'decodeJwt').mockReturnValue({ email: 'test@example.com' })
        render(<Nav />)
        expect(screen.getByText('test@example.com')).toBeInTheDocument()
    })

    test('logout button clears tokens', () => {
        const clearMock = jest.spyOn(auth, 'clearTokens').mockImplementation(() => {})
        jest.spyOn(auth, 'getIdToken').mockReturnValue('fake')
        jest.spyOn(auth, 'decodeJwt').mockReturnValue({ email: 'test@example.com' })
        render(<Nav />)
        fireEvent.click(screen.getByText('Logout'))
        expect(clearMock).toHaveBeenCalled()
    })
})
