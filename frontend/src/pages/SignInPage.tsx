import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { API_BASE } from '../services/api'

function SignInPage() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')
  const [loginError, setLoginError] = useState<string | null>(null)
  const [isSigningIn, setIsSigningIn] = useState(false)

  const handleUsernamePasswordLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLoginError(null)
    setIsSigningIn(true)

    try {
      const body = new URLSearchParams()
      body.set('username', username)
      body.set('password', password)

      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body,
      })

      const payload = await response.json().catch(() => null)

      if (!response.ok) {
        throw new Error(payload?.detail || 'Invalid username or password')
      }

      if (payload?.access_token) {
        window.localStorage.setItem('ai-portfolio-token', payload.access_token)
        window.localStorage.setItem('ai-portfolio-user', JSON.stringify(payload.user ?? {}))
        navigate('/', { replace: true })
        return
      }

      throw new Error('Login response missing access token')
    } catch (error) {
      setLoginError(String(error instanceof Error ? error.message : error))
    } finally {
      setIsSigningIn(false)
    }
  }

  return (
    <div className="signin-shell">
      <div className="signin-backdrop signin-backdrop-one" />
      <div className="signin-backdrop signin-backdrop-two" />

      <main className="signin-card">
        <section className="signin-brand-panel">
          <div className="signin-kicker">Enterprise Client Experience</div>
          <h1>Portfolio intelligence built for board-level clarity</h1>
          <p>
            Sign in with your organization’s identity provider to access a premium dashboard for upload validation,
            portfolio health, and branch performance.
          </p>
        </section>

        <section className="signin-form-panel">
          <div className="signin-form-header">
            <span className="signin-badge">Secure Access</span>
            <h2>Sign in with username and password</h2>
            <p>Use your role credentials to access the dashboard.</p>
          </div>

          <form className="signin-form" onSubmit={handleUsernamePasswordLogin}>
            <label className="form-field">
              <span>Username</span>
              <input
                type="text"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                placeholder="Enter username"
                autoComplete="username"
              />
            </label>

            <label className="form-field">
              <span>Password</span>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Enter password"
                autoComplete="current-password"
              />
            </label>

            {loginError && <div className="signin-error">{loginError}</div>}

            <button type="submit" className="demo-access-button" disabled={isSigningIn}>
              {isSigningIn ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

        </section>
      </main>
    </div>
  )
}

export default SignInPage