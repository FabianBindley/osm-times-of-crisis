import React, { useState } from "react";
import "./App.css";
import Maps from "./Maps";
import "antd/dist/reset.css"; // Ant Design styles
import { Menu } from "antd";
import ChangeDensityMapping from "./ChangeDensityMapping";
import ChangeCounting from "./ChangeCounting";
import Tags from "./Tags";

function App() {
  const [currentTab, setCurrentTab] = useState(localStorage.getItem("currentTab") ? localStorage.getItem("currentTab") : "changeDensityMapping");

  // Handle menu click
  const handleMenuClick = (e) => {
    setCurrentTab(e.key);
    localStorage.setItem("currentTab",e.key)
  };

  return (
    <div className="app">
      <h1 style={{ margin: "1em" }}>
        Visualising OSM crowdsourcing behaviour during natural disasters
      </h1>
      
      {/* Ant Design Menu */}
      <Menu
        onClick={handleMenuClick}
        selectedKeys={[currentTab]}
        mode="horizontal"
        style={{ marginBottom: "1em" }}
      >
        <Menu.Item key="changeCounting">Change Counting</Menu.Item>
        <Menu.Item key="changeDensityMapping">Change Density Mapping</Menu.Item>
        <Menu.Item key="tagWordCloud">Tag Word Cloud</Menu.Item>
      </Menu>

      {/* Conditional Rendering Based on Selected Tab */}
      <div>
        {currentTab === "changeCounting" && <ChangeCounting />}
        {currentTab === "changeDensityMapping" && <ChangeDensityMapping />}
        {currentTab === "tagWordCloud" && <Tags />}
      </div>
    </div>
  );
}

export default App;
