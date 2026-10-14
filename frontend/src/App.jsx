import { useState } from 'react'
import './App.css'

function App() {
  const [resume, setResume] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleAnalyze() {
    setError('')
    setProfile(null)

    if (!resume) {
      setError('Please select a PDF resume first.')
      return
    }

    const formData = new FormData()
    formData.append('file', resume)

    setLoading(true)

    try {
      const response = await fetch(
        'http://127.0.0.1:8000/api/resume/parse',
        {
          method: 'POST',
          body: formData,
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : 'Unable to parse this resume.'
        )
      }

      setProfile(data)
    } catch (err) {
      setError(
        err instanceof TypeError
          ? 'Could not reach the backend. Check that it is running.'
          : err.message
      )
    } finally {
      setLoading(false)
    }
  }

  function scrollToAnalyzer() {
    document
      .getElementById('analyze')
      ?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div className="app">
      <header className="navbar">
        <h2>AI Career Coach</h2>

        <nav>
          <a href="#home">Home</a>
          <a href="#analyze">Resume Analyzer</a>
          <a href="#jobs">Job Matches</a>
        </nav>
      </header>

      <main>
        <section className="hero-section" id="home">
          <div className="hero-text">
            <h1>Build a stronger resume. Find better job matches.</h1>

            <p>
              Upload your resume, compare it with job descriptions, and receive
              personalized feedback to help improve your career opportunities.
            </p>

            <button type="button" onClick={scrollToAnalyzer}>
              Get Started
            </button>
          </div>
        </section>

        <section className="analyzer-section" id="analyze">
          <h2>Resume Analyzer</h2>

          <p>
            Upload your resume and enter a target job description to see how
            well your skills match.
          </p>

          <div className="form-card">
            <label htmlFor="resume">Upload Resume</label>

            <input
              id="resume"
              type="file"
              accept=".pdf"
              disabled={loading}
              onChange={(event) => {
                setResume(event.target.files?.[0] ?? null)
                setProfile(null)
                setError('')
              }}
            />

            {resume && (
              <p>
                <strong>Selected file:</strong> {resume.name}
              </p>
            )}

            <label htmlFor="jobDescription">
              Target Job Description
            </label>

            <textarea
              id="jobDescription"
              placeholder="Paste a job description here..."
              rows="8"
              disabled={loading}
            />

            <button
              type="button"
              onClick={handleAnalyze}
              disabled={loading}
            >
              {loading ? 'Parsing Resume...' : 'Parse Resume'}
            </button>

            {error && (
              <p role="alert" className="error-message">
                {error}
              </p>
            )}

            {profile && (
              <div className="parsed-resume" aria-live="polite">
                <h3>Parsed Resume</h3>

                <p>
                  <strong>Name:</strong>{' '}
                  {profile.name || 'Not found'}
                </p>

                <p>
                  <strong>Email:</strong>{' '}
                  {profile.email || 'Not found'}
                </p>

                <p>
                  <strong>Phone:</strong>{' '}
                  {profile.phone || 'Not found'}
                </p>

                <p>
                  <strong>Skills:</strong>{' '}
                  {profile.skills?.length
                    ? profile.skills.join(', ')
                    : 'None detected'}
                </p>

                <details>
                  <summary>View all parsed information</summary>

                  <pre
                    style={{
                      whiteSpace: 'pre-wrap',
                      overflowWrap: 'anywhere',
                    }}
                  >
                    {JSON.stringify(profile, null, 2)}
                  </pre>
                </details>
              </div>
            )}
          </div>
        </section>

        <section className="results-section" id="jobs">
          <h2>Analysis Results</h2>

          <div className="results-grid">
            <div className="result-card">
              <h3>Match Score</h3>
              <p>
                Job matching will appear here once the matching system is
                connected to the backend.
              </p>
            </div>

            <div className="result-card">
              <h3>Matching Skills</h3>
              <p>
                Matching skills will appear here after job matching is
                connected.
              </p>
            </div>

            <div className="result-card">
              <h3>Missing Skills</h3>
              <p>
                Potential skill gaps will appear here after job matching is
                connected.
              </p>
            </div>

            <div className="result-card">
              <h3>Resume Feedback</h3>
              <p>
                AI-generated recommendations will appear here in a future
                integration step.
              </p>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App