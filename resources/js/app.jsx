import React from "react";
import ReactDOM from "react-dom/client";
import '../css/style.css';
import Navbar from './components/Navbar';
import JobList from './components/JobList';
import Sidebar from './components/Sidebar';

function App() {
  return (
    <div className="app">
      <Navbar />

      <div className="container">
        <div className="main">
          <h2 className="page-title">Available Job Openings</h2>

          {/* Search Bar */}
          <div className="search-bar">
            <div className="search-input-wrap">
              <span className="search-icon">&#128269;</span>
              <input type="text" placeholder="Search job title, company, or skills..." />
            </div>
            <select>
              <option value="">Location</option>
              <option>Remote</option>
              <option>San Francisco, CA</option>
              <option>New York, NY</option>
            </select>
            <div className="category-select-wrap">
              <label className="category-label">Job Category</label>
              <select className="category-select">
                <option>Engineering, Marketing, Design</option>
                <option>Engineering</option>
                <option>Marketing</option>
                <option>Design</option>
              </select>
            </div>
            <label className="remote-toggle">
              <input type="checkbox" />
              Remote Only
            </label>
          </div>

          <JobList />
        </div>

        <Sidebar />
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("app")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

export default App;