function MatchCircle({ percent, color }) {
  const r = 20;
  const circ = 2 * Math.PI * r;
  const offset = circ - (percent / 100) * circ;
  return (
    <svg width="52" height="52" viewBox="0 0 52 52">
      <circle cx="26" cy="26" r={r} fill="none" stroke="#e5e7eb" strokeWidth="4" />
      <circle
        cx="26" cy="26" r={r}
        fill="none"
        stroke={color}
        strokeWidth="4"
        strokeDasharray={circ}
        strokeDashoffset={offset}
        strokeLinecap="round"
        transform="rotate(-90 26 26)"
      />
      <text x="26" y="31" textAnchor="middle" fontSize="11" fontWeight="700" fill={color}>
        {percent}%
      </text>
    </svg>
  );
}

function JobCard({ title, company, companyLogo, location, postedAt, matchPercent, matchLabel, tags, description }) {
  const color = matchPercent >= 95 ? "#22c55e" : matchPercent >= 80 ? "#eab308" : "#f97316";

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-header-left">
          <h3 className="card-title">{title}</h3>
          <div className="company-row">
            {companyLogo
              ? <img src={companyLogo} alt={company} className="company-logo" />
              : <div className="company-logo-placeholder">{company[0]}</div>
            }
            <span className="company-name">{company}</span>
          </div>
          <div className="meta-row">
            <span className="meta-item">&#128205; {location}</span>
            <span className="meta-item">&#128197; {postedAt}</span>
          </div>
        </div>
        <div className="match-wrap">
          <span className="ai-badge">AI</span>
          <MatchCircle percent={matchPercent} color={color} />
          <span className="match-label" style={{ color }}>{matchLabel}</span>
        </div>
      </div>

      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${matchPercent}%`, backgroundColor: color }} />
      </div>

      <div className="tags">
        {tags.map((tag) => <span key={tag}>{tag}</span>)}
      </div>

      {description && <p className="card-desc">{description}</p>}

      <div className="buttons">
        <button className="details">View Details</button>
        <button className="apply">Apply Now</button>
      </div>
    </div>
  );
}

export default JobCard;