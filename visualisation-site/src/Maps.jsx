import React, { useState } from "react";
import { Select } from "antd"; 
import Map from './Map'
import "./App.css";

const maps = [
    { title: "Emilia Romagna Floods | 2023", disaster_id: 2 },
    { title: "Haiti Earthquake | 2010", disaster_id: 3},
    { title: "Haiti Earthquake and Hurricane Grace | 2021", disaster_id: 5},
    { title: "Nepal Earthquake | 2015", disaster_id: 6},
  ];

const additional_maps = [
    { title: "Broxbourne (All good) | 2024", disaster_id: 1 },
    { title: "Haiti Hurricane Matthew | 2016", disaster_id: 4},
]


function Maps() {

    const [resolution, setResolution] = useState("7")
    const [mapStyle, setMapStyle] = useState("change_count")

    const handleResolutionChange = (value) => {
        setResolution(value);
    };

    const handleMapStyleChange = (value) => {
        setMapStyle(value);
    };


    return (
        <>  
            <p>
                Maps are generated using Folium and OpenStreetMap data, and Uber H3 Hexagons
            </p>
            <div className="maps-header">
                <div style={{ marginBottom: 20 }}>
                    <label style={{ marginLeft: 10 }}>Map Hexagon Resolution:</label>
                    <Select
                        defaultValue={resolution}
                        style={{ width: 60, marginLeft: 10 }}
                        onChange={handleResolutionChange}
                    >
                        <Option value="5">5</Option>
                        <Option value="6">6</Option>
                        <Option value="7">7</Option>
                        <Option value="8">8</Option>
                        <Option value="9">9</Option>
                    </Select>
                </div>

                <div style={{ marginBottom: 20 }}>
                    <label style={{ marginLeft: 10 }}>Map Style:</label>
                    <Select
                        defaultValue={mapStyle}
                        style={{ width: 200, marginLeft: 10 }}
                        onChange={handleMapStyleChange}
                    >
                        <Option value="change_count">Change count</Option>
                        <Option value="percentage_difference">Change % Difference</Option>

                    </Select>
                </div>

            </div>

            {maps.map((map, index) => (
                <Map index={index} map={map} resolution={resolution} mapStyle={mapStyle}/>
            ))}

            <h2>Additional Maps</h2>
            {additional_maps.map((map, index) => (
                <Map index={index} map={map} resolution={resolution} mapStyle={mapStyle}/>
            ))}
        </>
    );
  }
  
  export default Maps;
  