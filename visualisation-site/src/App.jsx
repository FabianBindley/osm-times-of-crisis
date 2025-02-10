import React, { useState, useEffect } from "react";
import "./App.css";
import Maps from "./Maps";
import "antd/dist/reset.css"; // Ant Design styles
import { Menu } from "antd";
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from "react-router-dom";

import ChangeDensityMapping from "./ChangeDensityMapping";
import ChangeCounting from "./ChangeCounting";
import Tags from "./Tags";
import TagCorrelation from "./TagCorrelation"
import About from "./About";
import GeneralStatistics from "./GeneralSatistics";
import NotFound from "./NotFound";
import GiniCoefficient from "./GiniCoefficient";


function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

function AppContent() {

  const navigate = useNavigate();
  const location = useLocation();

  const currentPath = location.pathname.substring(1) || "about";

  const validTabs = [
    "generalStatistics",
    "changeCounting",
    "changeDensityMapping",
    "changeDensityInequality",
    "tagKeysValues",
    "tagCorrelation",
    "about",
  ];


  const isValidTab = validTabs.includes(currentPath);

  const [currentTab, setCurrentTab] = useState(localStorage.getItem("currentTab") ? localStorage.getItem("currentTab") : "about");

  useEffect(() => {
    if (isValidTab) {
      setCurrentTab(currentPath); 
    } else {
      setCurrentTab("404"); 
    }
  }, [currentPath]);

  // Handle menu click
  const handleMenuClick = (e) => {
    setCurrentTab(e.key);
    localStorage.setItem("currentTab",e.key)
    navigate(`/${e.key}`);
  };

  return (
    <div className="app">
      <h1 style={{ margin: "0.5em" }}>
        Visualising OSM crowdsourcing behaviour during natural disasters
      </h1>
      

      <Menu
        onClick={handleMenuClick}
        selectedKeys={[currentTab]}
        mode="horizontal"
        style={{ marginBottom: "1em" }}
      >
        <Menu.Item key="generalStatistics">General Statistics</Menu.Item>
        <Menu.Item key="changeCounting">Change Counting</Menu.Item>
        <Menu.Item key="changeDensityMapping">Change Density Mapping</Menu.Item>
        <Menu.Item key="changeDensityInequality">Change Density Inequality</Menu.Item>
        <Menu.Item key="tagKeysValues">Tag Keys and Values</Menu.Item>
        <Menu.Item key="tagCorrelation">Tag Correlation</Menu.Item>
        <Menu.Item key="about">About</Menu.Item>
      </Menu>

      {/* Conditional Rendering Based on Selected Tab */}
      <div>
        {currentTab === "generalStatistics" && <GeneralStatistics />}
        {currentTab === "changeCounting" && <ChangeCounting />}
        {currentTab === "changeDensityMapping" && <ChangeDensityMapping />}
        {currentTab === "changeDensityInequality" && <GiniCoefficient/>}
        {currentTab === "tagKeysValues" && <Tags />}
        {currentTab === "tagCorrelation" && <TagCorrelation />}
        {currentTab === "about" && <About />}
        {currentTab === "404" && <NotFound />}
      </div>
    </div>
  );
}

export default App;
