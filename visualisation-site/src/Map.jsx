import React, { useState, useEffect, useRef, memo } from "react";
import "./App.css";

const Map = memo(function Map({ index, map, resolution, mapStyle, interval, lazyLoading }) {
  const [isVisible, setIsVisible] = useState(false);
  const mapRef = useRef();

  // Intersection Observer to track visibility
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsVisible(entry.isIntersecting); // Update visibility based on intersection
      },
      { threshold: 0.01 } // Trigger when 5% of the element is visible
    );

    if (mapRef.current) {
      observer.observe(mapRef.current);
    }

    return () => {
      if (mapRef.current) {
        observer.unobserve(mapRef.current);
      }
    };
  }, []);

  var mapPath = "HELLO";
  if (mapStyle === "count_changes")
  {
      // Construct the map path
    mapPath = `ChangeDensityMapping/disaster${map.disaster_id}/charts/${interval.start}_${interval.imm}_${interval.end}_${resolution}_${mapStyle}.html`;
  }

  else
  {
      // Construct the map path
      if (interval.imm == "60" && interval.end == "0" && interval.post_only == false)
      {
        mapPath = `ChangeDensityMapping/disaster${map.disaster_id}/charts/365_60_365_${resolution}_pre_imm_${mapStyle}.html`;
      } else {
        mapPath = `ChangeDensityMapping/disaster${map.disaster_id}/charts/365_60_365_${resolution}_pre_post_${mapStyle}.html`;
      }
  
  }

  console.log(mapPath);

  // Render the map or a placeholder
  return (
    <>
      <h2>{map.title}</h2>
      <div key={index} className="iframe-container-density" ref={mapRef}>
        {isVisible || !lazyLoading ? (
          <iframe
            src={mapPath}
            title={map.title}
            style={{ width: "100%", height: "100%", border: "none" }}
          ></iframe>
        ) : (
          <div
            style={{
              width: "100%",
              height: "500px",
              backgroundColor: "#f0f0f0",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              color: "#555",
              fontSize: "16px",
              border: "1px solid #ddd",
            }}
          >
            <p>Loading...</p>
          </div>
        )}
      </div>
    </>
  );
});

export default Map;
