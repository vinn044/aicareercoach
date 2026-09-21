import './App.css'

function App() {
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

            <button>Get Started</button>
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
              accept=".pdf,.doc,.docx"
            />

            <label htmlFor="jobDescription">
              Target Job Description
            </label>

            <textarea
              id="jobDescription"
              placeholder="Paste a job description here..."
              rows="8"
            ></textarea>

            <button>Analyze Resume</button>
          </div>
        </section>

        <section className="results-section">
          <h2>Analysis Results</h2>

          <div className="results-grid">
            <div className="result-card">
              <h3>Match Score</h3>
              <p>Results will appear here.</p>
            </div>

            <div className="result-card">
              <h3>Matching Skills</h3>
              <p>Your matching skills will appear here.</p>
            </div>

            <div className="result-card">
              <h3>Missing Skills</h3>
              <p>Potential skill gaps will appear here.</p>
            </div>

            <div className="result-card">
              <h3>Resume Feedback</h3>
              <p>AI-generated recommendations will appear here.</p>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App