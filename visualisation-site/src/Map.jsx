import React, { memo } from "react";
import "./App.css";

const Map = memo(function Map({ index, map, resolution, mapStyle, interval }) {
  // Construct the map path
  //console.log("start: "+interval.start)
  //console.log("end: "+interval.end)
  const map_path = `ChangeDensityMapping/disaster${map.disaster_id}/charts/${interval.start}_${interval.end}_${resolution}_${mapStyle}.html`;

  //console.log("Rendering Map:", map_path);

  // Render the map with iframe
  return (
    <>
      <h2>{map.title}</h2>
      <div key={index} className="iframe-container">
          <iframe src={map_path} title={map.title}></iframe>
      </div>
    </>
  );
});

export default Map;
