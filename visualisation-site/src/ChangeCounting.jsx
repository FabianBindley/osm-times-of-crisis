import React from "react";
import "./App.css";
import { useState } from "react";
import Graph from "./Graph";
import { Select, Switch } from "antd"; 

function ChangeCounting() {
  
  const [interval, setInterval] = useState({start:"365", end:"365"})
  const [graphStyle, setGraphStyle] = useState("count_changes")
  const [periodLength, setPeriodLength] = useState("week")
  const [postOnly, setPostOnly] = useState(localStorage.getItem("postOnly")=="true" ? true : false);
  
  const intervalMap = {
    "365-365": { start: "365", end: "365" },
    "180-365": { start: "180", end: "365" },
    "0-365": { start: "90", end: "365" },
    "0-30": { start: "90", end: "180" },
  };

  const graphs = [
    { title: "Emilia Romagna Floods | 2023", disaster_id: 2 },
    { title: "Haiti Earthquake | 2010", disaster_id: 3},
    { title: "Haiti Earthquake and Hurricane Grace | 2021", disaster_id: 5},
    { title: "Nepal Earthquake | 2015", disaster_id: 6},
  ];

const additional_graphs = [
    { title: "Broxbourne (All good) | 2024", disaster_id: 1 },
    { title: "Haiti Hurricane Matthew | 2016", disaster_id: 4},
]

  const count_change_intervals = [{start:"365", end:"365"},{start:"180", end:"365"},{start:"90", end:"365"},{start:"90", end:"180"}]

  const percent_difference_intervals = [{start:"365", end:"365"},{start:"180", end:"365"},{start:"90", end:"365"},{start:"90", end:"180"}]

  const handleIntervalChange = (key) => {
    // Map the key to the corresponding interval object
    setInterval(intervalMap[key]);
  };


  const handleGraphStyleChange = (value) => {
    setGraphStyle(value);

    // Check for valid intervals and resolutions based on map style
    const isValidInterval =
        value === "count_changes"
            ? count_change_intervals.some(
                  (item) => item.start === interval.start && item.end === interval.end
              )
            : percent_difference_intervals.some(
                  (item) => item.start === interval.start && item.end === interval.end
              );


    if (!isValidInterval) {
        console.log("Resetting interval and resolution to defaults");
        setInterval({ start: "365", end: "365" });
        setResolution("7");
    }
};


  const handlePeriodLengthChange = (value) => {
    setPeriodLength(value);
  };

  const handlePostOnlyChange = (checked) => {
        setPostOnly(checked);
        localStorage.setItem("postOnly", checked)
  }

  return (
    <>  
            <p>
                Maps are generated using the counts from the Postgres DB and Matplotlib
            </p>
            <div className="maps-header">

                <div style={{marginTop:5,marginBottom:5}}>
                    <label style={{ marginLeft: 20 }}>Graph Style:</label>
                    <Select
                        defaultValue={graphStyle}
                        style={{ width: 200, marginLeft: 10 }}
                        onChange={handleGraphStyleChange}
                    >
                        <Select.Option value="count_changes">Change count</Select.Option>
                        <Select.Option value="percent_difference_time_series">Change % Difference</Select.Option>

                    </Select>

                    
                </div>


                <div style={{marginTop:5,marginBottom:5}}>
                    <label style={{ marginLeft: 20 }}>Graph Intervals:</label>
                    <Select
                        defaultValue="365-365"
                        value={`${interval.start}-${interval.end}`}
                        style={{ width: 200, marginLeft: 10 }}
                        onChange={handleIntervalChange}
                    >
                        <Select.Option value="365-365">365 Before - 365 After</Select.Option>
                        <Select.Option value="180-365">180 Before - 365 After</Select.Option>
                        <Select.Option value="90-365">90 Before - 365 After</Select.Option>
                        <Select.Option value="90-180">90 Before - 180 After</Select.Option>
                    </Select>
                </div> 

            
                

                <div style={{marginTop:5,marginBottom:5}}>
                <label style={{ marginLeft: 20 }}>Period:</label>
                <Select
                    defaultValue={periodLength}
                    value={periodLength}
                    style={{ width: 100, marginLeft: 10 }}
                    onChange={handlePeriodLengthChange}
                >
                    <Select.Option value="day">Day</Select.Option>
                    <Select.Option value="week">Week</Select.Option>
                    <Select.Option value="month">Month</Select.Option>
                </Select>
                </div>

                { graphStyle == "percent_difference_time_series" ? 
                    <div style={{marginTop:5,marginBottom:5}}>
                    <label style={{ marginLeft: 20, marginRight: 10 }}>Post Disaster Only:</label>
                    <Switch checked={postOnly} onChange={handlePostOnlyChange} />
                </div> 
                : <></>}
                

                

            </div>

            {graphs.map((graph, index) => (
                <Graph index={index} graph={graph}  graphStyle={graphStyle} interval={interval} periodLength={periodLength} postOnly={postOnly}/>
            ))}

            <h2>Additional Graphs</h2>
            {additional_graphs.map((graph, index) => (
                <Graph index={index} graph={graph}  graphStyle={graphStyle} interval={interval} periodLength={periodLength}  postOnly={postOnly}/>
            ))}
    </>
  )
}

export default ChangeCounting;
