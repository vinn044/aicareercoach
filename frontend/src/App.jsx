import { useEffect, useState } from 'react'
import './App.css'
import CareerScene from './components/CareerScene'

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
        setJobsError(
          'Available jobs could not be loaded. Start the backend and refresh.'
        )
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

  function scrollToAnalyzer() {
    document
      .getElementById('analyze')
      ?.scrollIntoView({ behavior: 'smooth' })
  }

  const scorePercent = results?.top_match
    ? Math.max(0, Math.min(100, results.top_match.score * 100))
    : 0

  function getScoreClass(score) {
    if (score < 50) return 'score-low'
    if (score < 75) return 'score-medium'
    return 'score-high'
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
        {/* HERO */}
        <section className="hero-section" id="home">
          <div className="hero-text">
            <h1>Build a stronger resume. Find better job matches.</h1>

            <p>
              Upload your resume to see how it semantically matches the jobs in
              our current sample list.
            </p>

            <button type="button" onClick={scrollToAnalyzer}>
              Get Started
            </button>
          </div>

          <div className="hero-visual">
            <CareerScene />
          </div>
        </section>

        {/* AVAILABLE JOBS */}
        <section className="jobs-section" id="jobs">
          <div className="section-heading">
            <span className="section-label">Opportunities</span>

            <h2>Available Jobs for Matching</h2>

            <p>
              These are the eight sample jobs your uploaded resume will be
              ranked against.
            </p>
          </div>

          {jobsError && (
            <p className="message error-message" role="alert">
              {jobsError}
            </p>
          )}

          <div className="jobs-grid">
            {jobs.map((job) => (
              <article
                className="job-card"
                key={`${job.title}-${job.company}`}
              >
                <h3>{job.title}</h3>

                <p className="job-meta">
                  {job.company} · {job.location}
                </p>

                <p>{job.description}</p>
              </article>
            ))}
          </div>
        </section>

        {/* RESUME ANALYZER */}
        <section className="analyzer-section" id="analyze">
          <div className="section-heading">
            <span className="section-label">Resume Analysis</span>

            <h2>Find where your experience fits.</h2>

            <p>
              Upload a PDF resume and we’ll compare your experience against the
              available jobs using semantic matching.
            </p>
          </div>

          <div className="form-card">
            <label htmlFor="resume">Upload Resume</label>

            <input
              id="resume"
              type="file"
              accept=".pdf"
              disabled={loading}
              onChange={(event) => {
                setResume(event.target.files?.[0] ?? null)
                setResults(null)
                setError('')
              }}
            />

            {resume && (
              <p className="selected-file">
                Selected file: <strong>{resume.name}</strong>
              </p>
            )}

            <button
              type="button"
              onClick={handleAnalyze}
              disabled={loading}
            >
              {loading ? 'Analyzing Resume...' : 'Analyze Resume'}
            </button>

            {error && (
              <p className="message error-message" role="alert">
                {error}
              </p>
            )}

            {results && (
              <div className="parsed-resume" aria-live="polite">
                <h3>Resume Profile</h3>

                <p>
                  <strong>Name:</strong>{' '}
                  {results.profile?.name || 'Not found'}
                </p>

                <p>
                  <strong>Skills:</strong>{' '}
                  {results.profile?.skills?.length
                    ? results.profile.skills.join(', ')
                    : 'None detected'}
                </p>
              </div>
            )}
          </div>
        </section>

        {/* ANALYSIS RESULTS */}
        <section className="results-section">
          <div className="section-heading">
            <span className="section-label">Your Results</span>
            <h2>Analysis Results</h2>
          </div>

          <div className="results-grid">
            <div className="result-card">
              <h3>Similarity Score</h3>

              {results?.top_match ? (
                <>
                  <p
                    className={`score ${getScoreClass(scorePercent)}`}
                  >
                    {scorePercent.toFixed(1)}%
                  </p>

                  <div
                    className={`score-meter ${getScoreClass(scorePercent)}`}
                    role="progressbar"
                    aria-label="Similarity score"
                    aria-valuemin="0"
                    aria-valuemax="100"
                    aria-valuenow={scorePercent}
                    style={{ '--score': `${scorePercent}%` }}
                  />

                  <p>
                    Top match:{' '}
                    <strong>{results.top_match.title}</strong>
                  </p>

                  <p className="score-note">
                    A relative score for these sample jobs, not a hiring
                    probability.
                  </p>
                </>
              ) : (
                <p>
                  Upload a resume to see your top semantic similarity score.
                </p>
              )}
            </div>

            <div className="result-card">
              <h3>Matching Skills</h3>

              {results ? (
                results.matching_skills?.length > 0 ? (
                  <ul className="skill-list">
                    {results.matching_skills.map((skill) => (
                      <li key={skill}>{skill}</li>
                    ))}
                  </ul>
                ) : (
                  <p>
                    No recognized skills overlap with the top job yet.
                  </p>
                )
              ) : (
                <p>
                  Shared skills with the top-ranked job will appear here.
                </p>
              )}
            </div>
          </div>

          {results?.ranked_jobs?.length > 0 && (
            <div className="rankings" aria-live="polite">
              <div className="rankings-heading">
                <h3>Your Ranked Job Matches</h3>

                <p>
                  All available jobs, ordered by semantic similarity.
                </p>
              </div>

              <ol className="ranking-list">
                {results.ranked_jobs.map((job, index) => {
                  const jobScore = Math.max(
                    0,
                    Math.min(100, job.score * 100)
                  )

                  return (
                    <li key={`${job.title}-${job.company}`}>
                      <div className="ranking-position">
                        {String(index + 1).padStart(2, '0')}
                      </div>

                      <div className="ranking-info">
                        <strong>{job.title}</strong>

                        <span>
                          {job.company} · {job.location}
                        </span>
                      </div>

                      <span
                        className={`ranking-score ${getScoreClass(jobScore)}`}
                      >
                        {jobScore.toFixed(1)}%
                      </span>
                    </li>
                  )
                })}
              </ol>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

export default App