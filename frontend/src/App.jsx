import { useEffect, useState } from 'react'
import './App.css'

const API_URL = 'http://localhost:8000/api'

function App() {
  const [resume, setResume] = useState(null)
  const [jobs, setJobs] = useState([])
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [jobsError, setJobsError] = useState('')

  useEffect(() => {
    // The backend is the source of truth for the jobs displayed and ranked.
    async function loadJobs() {
      try {
        const response = await fetch(`${API_URL}/jobs`)
        const data = await response.json()
        if (!response.ok) {
          throw new Error('Unable to load available jobs.')
        }
        setJobs(data.jobs)
      } catch {
        setJobsError('Available jobs could not be loaded. Start the backend and refresh.')
      }
    }

    loadJobs()
  }, [])

  async function handleAnalyze() {
    setError('')
    setResults(null)

    if (!resume) {
      setError('Please select a PDF resume first.')
      return
    }

    const formData = new FormData()
    formData.append('file', resume)
    setLoading(true)

    try {
      const response = await fetch(`${API_URL}/resume/match`, {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : 'Unable to analyze this resume.'
        )
      }

      setResults(data)
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

  const scorePercent = results
    ? Math.max(0, Math.min(100, results.top_match.score * 100))
    : 0

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
            Upload your resume to see how it semantically matches the jobs in
            our current sample list.
            </p>

            <button>Get Started</button>
          </div>
        </section>

        <section className="jobs-section" id="jobs">
          <h2>Available Jobs for Matching</h2>
          <p>These are the eight sample jobs your uploaded resume will be ranked against.</p>

          {jobsError && <p className="message error-message" role="alert">{jobsError}</p>}

          <div className="jobs-grid">
            {jobs.map((job) => (
              <article className="job-card" key={`${job.title}-${job.company}`}>
                <h3>{job.title}</h3>
                <p className="job-meta">{job.company} · {job.location}</p>
                <p>{job.description}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="analyzer-section" id="analyze">
          <h2>Resume Analyzer</h2>

          <p>
            Upload a PDF resume to rank it against the available jobs.
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

            <button
              type="button"
              onClick={handleAnalyze}
              disabled={loading}
            >
              {loading ? 'Analyzing Resume...' : 'Analyze Resume'}
            </button>

            {error && <p className="message error-message" role="alert">{error}</p>}

            {results && (
              <div aria-live="polite">
                <h3>Parsed Resume</h3>
                <p><strong>Name:</strong> {results.profile.name || 'Not found'}</p>
                <p>
                  <strong>Skills:</strong>{' '}
                  {results.profile.skills.join(', ') || 'None detected'}
                </p>
              </div>
            )}
          </div>
        </section>

        <section className="results-section">
          <h2>Analysis Results</h2>

          <div className="results-grid">
            <div className="result-card">
              <h3>Similarity Score</h3>
              {results ? (
                <>
                  <p className="score">{scorePercent.toFixed(1)}%</p>
                  <div
                    className="score-meter"
                    role="progressbar"
                    aria-label="Similarity score"
                    aria-valuemin="0"
                    aria-valuemax="100"
                    aria-valuenow={scorePercent}
                    style={{ '--score': `${scorePercent}%` }}
                  />
                  <p>Top match: {results.top_match.title}</p>
                  <p className="score-note">A relative score for these sample jobs, not a hiring probability.</p>
                </>
              ) : <p>Upload a resume to see the top semantic similarity score.</p>}
            </div>

            <div className="result-card">
              <h3>Matching Skills</h3>
              {results ? (
                results.matching_skills.length > 0
                  ? <ul className="skill-list">{results.matching_skills.map((skill) => <li key={skill}>{skill}</li>)}</ul>
                  : <p>No recognized skills overlap with the top job yet.</p>
              ) : <p>Shared skills with the top-ranked job will appear here.</p>}
            </div>
          </div>

          {results && (
            <div className="rankings" aria-live="polite">
              <h3>Your Ranked Job Matches</h3>
              <p>All available jobs, ordered by semantic similarity.</p>
              <ol className="ranking-list">
                {results.ranked_jobs.map((job) => (
                  <li key={`${job.title}-${job.company}`}>
                    <div>
                      <strong>{job.title}</strong>
                      <span>{job.company} · {job.location}</span>
                    </div>
                    <span className="ranking-score">{(job.score * 100).toFixed(1)}%</span>
                  </li>
                ))}
              </ol>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

export default App
