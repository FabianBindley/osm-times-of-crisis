import React from "react";
import "./App.css";
import Maps from "./Maps";
import 'antd/dist/reset.css'; // Ant Design styles



function App() {
  return (
    <div className="app">
      <h1 style={{margin: '1em'}}>Visualising OSM crowdsourcing behaviour during natural disasters</h1>
      <Maps/>
    </div>  
  );
}

export default App;
