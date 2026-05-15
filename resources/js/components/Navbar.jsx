function Navbar() {
  return (
    <div className="navbar">
      <div className="navbar-brand">
        <div className="brand-icon">P</div>
      </div>

      <ul>
        <li>Home</li>
        <li className="active">Find Jobs</li>
        <li>My Applications</li>
        <li>Messages</li>
      </ul>

      <div className="user">
        <img
          src="https://i.pravatar.cc/32?img=12"
          alt="John Doe"
          className="user-avatar"
        />
        <span className="user-name">John Doe</span>
        <span className="user-chevron">&#8964;</span>
      </div>
    </div>
  );
}

export default Navbar;