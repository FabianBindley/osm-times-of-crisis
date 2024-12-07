import React from "react";
import "./App.css";

function Map({index, map, resolution, mapStyle}) {
    const map_path = `maps/${mapStyle}/disaster_map_${map.disaster_id}_res_${resolution}.html`

    return (
        <>
            <h2>{map.title}</h2>
            <div key={index} className="iframe-container">
            <iframe src={map_path} title={map.title}></iframe>
            </div>
        </>
    );
  }
  
  export default Map;
  