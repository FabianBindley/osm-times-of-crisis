import React, { useState } from "react";
import { Select, Switch } from "antd"; 
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
    const [mapStyle, setMapStyle] = useState("count_changes")
    const [interval, setInterval] = useState({start:"365", end:"365"})
    const [lazyLoading, setLazyLoading] = useState(localStorage.getItem("lazyLoading")=="false" ? false : true);

    const intervalMap = {
        "365-365": { start: "365", end: "365" },
        "180-365": { start: "180", end: "365" },
        "0-365": { start: "0", end: "365" },
        "0-30": { start: "0", end: "30" },
      };

    const count_change_intervals = [{start:"365", end:"365"},{start:"180", end:"365"},{start:"0", end:"365"},{start:"0", end:"30"}]
    const count_change_resolutions = ["6", "7", "8"]

    const percent_difference_intervals = [{start:"365", end:"365"},{start:"180", end:"365"}]
    const percent_difference_resolutions = ["6", "7"]
      

    const handleResolutionChange = (value) => {
        setResolution(value);
    };

    const handleMapStyleChange = (value) => {
        setMapStyle(value);

        // Check for valid intervals and resolutions based on map style
        const isValidInterval =
            value === "count_changes"
                ? count_change_intervals.some(
                      (item) => item.start === interval.start && item.end === interval.end
                  )
                : percent_difference_intervals.some(
                      (item) => item.start === interval.start && item.end === interval.end
                  );
    
        const isValidResolution =
            value === "count_changes"
                ? count_change_resolutions.includes(resolution)
                : percent_difference_resolutions.includes(resolution);
    
        if (!isValidInterval || !isValidResolution) {
            console.log("Resetting interval and resolution to defaults");
            setInterval({ start: "365", end: "365" });
            setResolution("7");
        }
    };

    const handleIntervalChange = (key) => {
        // Map the key to the corresponding interval object
        setInterval(intervalMap[key]);
      };

      const handleChangeLazyLoading = (checked) => {
        setLazyLoading(checked);
        localStorage.setItem("lazyLoading", checked)
      };


    return (
        <>  
            <p>
                Maps are generated using Folium and OpenStreetMap data, and Uber H3 Hexagons
            </p>
            <div className="maps-header">

                <div style={{ marginBottom: 20 }}>
                    <label style={{ marginLeft: 20 }}>Map Style:</label>
                    <Select
                        defaultValue={mapStyle}
                        style={{ width: 200, marginLeft: 10 }}
                        onChange={handleMapStyleChange}
                    >
                        <Select.Option value="count_changes">Change count</Select.Option>
                        <Select.Option value="percent_difference">Change % Difference</Select.Option>

                    </Select>

                    
                </div>
                {
                    mapStyle == "count_changes" ? 
                    <div style={{ marginBottom: 20 }}>
                        <label style={{ marginLeft: 10 }}>Resolution:</label>
                        <Select
                            defaultValue={resolution}
                            value={resolution}
                            style={{ width: 60, marginLeft: 10 }}
                            onChange={handleResolutionChange}
                        >
                            <Select.Option value="6">6</Select.Option>
                            <Select.Option value="7">7</Select.Option>
                            <Select.Option value="8">8</Select.Option>
                        </Select>
                    </div> 
                    : 
                    <div style={{ marginBottom: 20 }}>
                        <label style={{ marginLeft: 10 }}>Resolution:</label>
                        <Select
                            defaultValue={resolution}
                            value={resolution}
                            style={{ width: 60, marginLeft: 10 }}
                            onChange={handleResolutionChange}
                        >
                            <Select.Option value="6">6</Select.Option>
                            <Select.Option value="7">7</Select.Option>
                        </Select>
                    </div> 
                    }

                {
                    mapStyle == "count_changes" ? 
                    <div style={{ marginBottom: 20 }}>
                        <label style={{ marginLeft: 20 }}>Map Intervals:</label>
                        <Select
                            defaultValue="365-365"
                            value={`${interval.start}-${interval.end}`}
                            style={{ width: 200, marginLeft: 10 }}
                            onChange={handleIntervalChange}
                        >
                            <Option value="365-365">365 Before - 365 After</Option>
                            <Option value="180-365">180 Before - 365 After</Option>
                            <Option value="0-365">0 Before - 365 After</Option>
                            <Option value="0-30">0 Before - 30 After</Option>
                        </Select>
                    </div> 
                    : 
                    <div style={{ marginBottom: 20 }}>
                        <label style={{ marginLeft: 20 }}>Map Intervals:</label>
                        <Select
                            defaultValue="365-365"
                            value={`${interval.start}-${interval.end}`}
                            style={{ width: 200, marginLeft: 10 }}
                            onChange={handleIntervalChange}
                        >
                            <Option value="365-365">365 Before - 365 After</Option>
                            <Option value="180-365">180 Before - 365 After</Option>
                        </Select>
                 </div>
            
                }
                
                <div style={{ marginBottom: 20 }}>
                    <label style={{ marginLeft: 150, marginRight: 10 }}>Lazy Loading:</label>
                    <Switch checked={lazyLoading} onChange={handleChangeLazyLoading} />
                </div> 

                

            </div>

            <div className="maps-header">

            </div>

            {maps.map((map, index) => (
                <Map index={index} map={map} resolution={resolution} mapStyle={mapStyle} interval={interval} lazyLoading={lazyLoading}/>
            ))}

            <h2>Additional Maps</h2>
            {additional_maps.map((map, index) => (
                <Map index={index} map={map} resolution={resolution} mapStyle={mapStyle} interval={interval} lazyLoading={lazyLoading}/>
            ))}
        </>
    );
  }
  
  export default Maps;
  