const RECOMMENDED = [
  {
    title: "Senior Full Stack Engineer",
    company: "TechCorp Solutions",
    logo: "https://via.placeholder.com/16/1d4ed8/ffffff?text=T",
    location: "San Francisco, CA",
    postedAt: "Posted 3 days ago",
    tags: ["Python", "React", "AWS", "SQL"],
  },
  {
    title: "Product Marketing Manager",
    company: "Global Analytics",
    logo: "https://via.placeholder.com/16/6366f1/ffffff?text=G",
    location: "New York, NY",
    postedAt: "Posted today",
    tags: ["Python", "Marketing", "SQL", "React"],
  },
];

function Sidebar() {
  return (
    <div className="sidebar">
      <h3>Recommended for You</h3>

      {RECOMMENDED.map((job, i) => (
        <div className="mini-card" key={i}>
          <p className="mini-title">{job.title}</p>
          <div className="mini-company-row">
            <img src={job.logo} alt={job.company} className="mini-logo" />
            <span className="mini-company">{job.company}</span>
          </div>
          <div className="mini-meta">
            <span>&#128205; {job.location}</span>
            <span>&#128197; {job.postedAt}</span>
          </div>
          <div className="tags mini-tags">
            {job.tags.map((t) => <span key={t}>{t}</span>)}
          </div>
          <div className="buttons mini-buttons">
            <button className="details">View Details</button>
            <button className="apply">Apply Now</button>
          </div>
        </div>
      ))}

      <div className="cv-banner">
        <h4>Your CV is 100% Complete</h4>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: "100%", backgroundColor: "#22c55e" }} />
        </div>
        <p>Your CV is 100% Complete</p>
        <button className="apply" style={{ width: "100%" }}>Apply Details</button>
      </div>
    </div>
  );
}

export default Sidebar;