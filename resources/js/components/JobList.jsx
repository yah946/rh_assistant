import JobCard from './JobCard';

const JOBS = [
  {
    title: "Senior Full Stack Engineer",
    company: "TechCorp Solutions",
    companyLogo: "https://via.placeholder.com/20/1d4ed8/ffffff?text=T",
    location: "San Francisco, CA",
    postedAt: "Posted 3 days ago",
    matchPercent: 95,
    matchLabel: "95% Match",
    tags: ["Python", "React", "AWS", "SQL"],
    description: "Senior full stack engineer and core responsibilities and accessing competencies in modern web stacks.",
  },
  {
    title: "Data Analyst",
    company: "Global Analytics",
    companyLogo: "https://via.placeholder.com/20/6366f1/ffffff?text=G",
    location: "Remote",
    postedAt: "Posted today",
    matchPercent: 95,
    matchLabel: "95% Match",
    tags: ["Poskent", "React"],
    description: "Provides analytics and analysis of the summaries with data analytics and acceleration tools.",
  },
  {
    title: "Product Marketing Manager",
    company: "Global Analytics",
    companyLogo: "https://via.placeholder.com/20/6366f1/ffffff?text=G",
    location: "New York, NY",
    postedAt: "Posted today",
    matchPercent: 98,
    matchLabel: "High Match",
    tags: ["Detht", "Marketing", "Engineer"],
    description: "Product marketing manager for marketing design and execute implementations and strategy.",
  },
  {
    title: "Data Analyst",
    company: "Global Analytics",
    companyLogo: "https://via.placeholder.com/20/6366f1/ffffff?text=G",
    location: "Remote",
    postedAt: "Posted 3 days ago",
    matchPercent: 95,
    matchLabel: "High Match",
    tags: ["Python", "React", "AWS", "SQL"],
    description: "Brief description meaning the core responsibilities to consectetism pobnitive tasks.",
  },
  {
    title: "Product Marketing",
    company: "Global Analytics",
    companyLogo: "https://via.placeholder.com/20/6366f1/ffffff?text=G",
    location: "Remote",
    postedAt: "Posted today",
    matchPercent: 95,
    matchLabel: "High Match",
    tags: ["Python", "Design", "SQL"],
    description: "Product marketing manager, to perform and competencies-jobs, analite service and management.",
  },
  {
    title: "Product Marketing Manager",
    company: "Global Analytics",
    companyLogo: "https://via.placeholder.com/20/6366f1/ffffff?text=G",
    location: "New York, NY",
    postedAt: "Posted today",
    matchPercent: 95,
    matchLabel: "High Match",
    tags: ["Python", "React", "AWS"],
    description: "Brief description manacist information and responsibilities monagations and productions.",
  },
];

function JobList() {
  return (
    <div className="job-list">
      {JOBS.map((job, i) => (
        <JobCard key={i} {...job} />
      ))}
    </div>
  );
}

export default JobList;