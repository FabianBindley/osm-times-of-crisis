import React from "react";
import { Link } from "react-router-dom";

const NotFound = () => {
  return (
    <div style={{ textAlign: "center", marginTop: "5rem" }}>
      <h1>404 - Page Not Found</h1>
      <p style={{textAlign:'center', marginTop:'2em', marginBottom:'2em'}}>The page/item you are looking for doesn't exist.</p>
      <Link to="/" style={{ textDecoration: "none", color: "blue" }}>
        Go Back Home
      </Link>
    </div>
  );
};

export default NotFound;
