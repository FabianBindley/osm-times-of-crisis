import React, { useState } from "react";
import { Select, Switch } from "antd"; 
import Map from './Map'
import "./App.css";

const maps = [
    { title: "Haiti Earthquake | 2010", disaster_id: 3},
    { title: "Texas Hurricane Harvey | 2017", disaster_id: 8},
    { title: "California Wildfires | 2020", disaster_id: 7},
    { title: "Haiti Earthquake and Hurricane Grace | 2021", disaster_id: 5},
    { title: "Nepal Earthquake | 2015", disaster_id: 6},
    { title: "Sulawesi, Indonesia Earthquake and Tsunami | 2018", disaster_id: 9},
    { title: "Atami, Japan Landslide | 2021", disaster_id: 14},
    { title: "Pakistan Floods | 2022", disaster_id: 13},
    { title: "Attica, Greece Wildfires | 2018", disaster_id: 10},
    { title: "Izmir, Turkey Earthquake and Tsunami | 2020", disaster_id: 11},
    { title: "Gaziantep, Turkey Earthquake | 2023", disaster_id: 12},
    { title: "Emilia Romagna Floods | 2023", disaster_id: 2 },
    { title: "Freetown, Sierra Leone Landslide | 2017", disaster_id: 18},
    { title: "Derna, Libya Dam Collapse Floods | 2023", disaster_id: 15},
    { title: "Malawi Hurricane Freddy | 2023", disaster_id: 16},
    { title: "Morocco Earthquake | 2023", disaster_id: 17},
  ];


const additional_maps = [
    //{ title: "Broxbourne (All good) | 2024", disaster_id: 1 },
    { title: "Haiti Hurricane Matthew | 2016", disaster_id: 4},
]



function ChangeDensityMapping() {

    const urlParams = new URLSearchParams(window.location.search);
    const validResolutions = ["6", "7", "8", "9"];
    const urlResolution = urlParams.get("res");
    const [resolution, setResolution] = useState(validResolutions.includes(urlResolution) ? urlResolution : "7");


    const validMapStyleParams = {
    count: "count_changes",
    percent: "percent_difference",
    };
    const urlMapStyleParam = urlParams.get("style");
    const [mapStyle, setMapStyle] = useState(validMapStyleParams[urlMapStyleParam] || "count_changes");


    const [interval, setInterval] = useState(mapStyle == "count_changes" ? {start:"365", imm:"60", end:"365", post_only: false} : { start: "0", imm:"60", end: "0", post_only: false })
    const [lazyLoading, setLazyLoading] = useState(localStorage.getItem("lazyLoading")=="false" ? false : true);

    const intervalMap = {
        "365-0-0": { start: "365", imm:"0", end: "0", post_only: false },
        "0-60-0": { start: "0", imm:"60", end: "0", post_only: false },
        "0-60-365": { start: "0", imm:"60", end: "365", post_only: true },
        "365-60-365": { start: "365", imm:"60", end: "365", post_only: false},
      };

    const count_change_intervals = [{ start: "365", imm:"0", end: "0" },{ start: "365", imm:"0", end: "0" },{ start: "365", imm:"0", end: "0" },{start:"365", imm:"60", end:"365"}]
    const count_change_resolutions = ["6", "7", "8", "9"]

    const percent_difference_intervals = [{start:"0", imm:"60", end:"0"},{start:"0", imm:"60", end:"365"}]
    const percent_difference_resolutions = ["6", "7", "8", "9"]
      

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
            if (value === "count_changes"){
                setInterval({ start: "365", imm:"60", end: "365", post_only: false });
            } else {
                setInterval({ start: "0", imm:"60", end: "0", post_only: false });
            }
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
                Maps are generated using Folium and OpenStreetMap data, and Uber H3 Hexagons. In all cases, the immediate period is set to 30 days.
            </p>
            <div className="maps-header">

            <div style={{marginTop:5,marginBottom:5}}>
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

                <div style={{marginTop:5,marginBottom:5}}>
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
                        <Select.Option value="9">9</Select.Option>
                    </Select>
                </div> 

                    

                {
                    mapStyle == "count_changes" ? 
                    <div style={{marginTop:5,marginBottom:5}}>
                        <label style={{ marginLeft: 20 }}>Map Intervals:</label>
                        <Select
                            defaultValue="365-60-365"
                            value={`${interval.start}-${interval.imm}-${interval.end}`}
                            style={{ width: 200, marginLeft: 10 }}
                            onChange={handleIntervalChange}
                        >
                            <Option value="365-60-365">All periods</Option>
                            <Option value="365-0-0">Pre</Option>
                            <Option value="0-60-0">Imm</Option>
                            <Option value="0-60-365">Post</Option>
                        </Select>
                    </div> 
                    : 
                    <div style={{marginTop:5,marginBottom:5}}>
                        <label style={{ marginLeft: 20 }}>Map Intervals:</label>
                        <Select
                            defaultValue="0-60-0"
                            value={`${interval.start}-${interval.imm}-${interval.end}`}
                            style={{ width: 200, marginLeft: 10 }}
                            onChange={handleIntervalChange}
                        >
                            <Option value="0-60-0">Pre/Imm</Option>
                            <Option value="0-60-365">Pre/Post</Option>
                        </Select>
                 </div>
            
                }
                
                <div style={{marginTop:5,marginBottom:5}}>
                    <label style={{ marginLeft: 20, marginRight: 10 }}>Lazy Loading:</label>
                    <Switch checked={lazyLoading} onChange={handleChangeLazyLoading} />
                </div> 

                

            </div>

            <div className="maps-header">

            </div>

            {maps.map((map, index) => (
                <Map index={index} map={map} resolution={resolution} mapStyle={mapStyle} interval={interval} lazyLoading={lazyLoading}/>
            ))}

   
            {/*
            <h2>Additional Maps</h2>
            {additional_maps.map((map, index) => (
                <Map index={index} map={map} resolution={resolution} mapStyle={mapStyle} interval={interval} lazyLoading={lazyLoading}/>
            ))}
                */}
        </>
    );
  }
  
  export default ChangeDensityMapping;
  