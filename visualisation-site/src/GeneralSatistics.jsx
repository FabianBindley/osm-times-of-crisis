import React, {useState} from 'react';
import "./App.css";
import { Image, Select } from 'antd';

export default function GeneralStatistics() {
      const [interval, setInterval] = useState({start:"365", end:"365"})
      const intervalMap = {
        "365-365": { start: "365", end: "365" },
        "1095-365": { start: "1095", end: "365" },
        "180-365": { start: "180", end: "365" },
        "90-365": { start: "90", end: "365" },
        "90-180": { start: "90", end: "180" },
      };
      const count_change_intervals = [{start:"365", end:"365"},{start:"1095", end:"365"},{start:"180", end:"365"},{start:"90", end:"365"},{start:"90", end:"180"}]
      const handleIntervalChange = (key) => {
        // Map the key to the corresponding interval object
        setInterval(intervalMap[key]);
      };

    return (
        <div>
            <div className="maps-header">
            <div style={{marginTop:5,marginBottom:5}}>
                    <label style={{ marginLeft: 20 }}>Graph Intervals:</label>
                    <Select
                        defaultValue="365-365"
                        value={`${interval.start}-${interval.end}`}
                        style={{ width: 200, marginLeft: 10 }}
                        onChange={handleIntervalChange}
                    >
                        <Select.Option value="365-365">365 Pre - 365 Post</Select.Option>
                        <Select.Option value="180-365">180 Pre - 365 Post</Select.Option>
                        <Select.Option value="1095-365">1095 Pre - 365 Post</Select.Option>
                    </Select>
                </div> 
            </div>
            <p>
                The following general statistics were computed for the selected period:
            </p>
            <div className="wordcloud-container">
                <div style={{width: '65%'}}>
                    <h2>Changes by period across all disasters</h2>
                    <Image
                    width="100%"
                    src={`ChangeCounting/summary/charts/${interval.start}_30_${interval.end}_changes_count_stacked_bar.png`}
                    />
                </div>
                <div style={{width: '35%'}}>
                    <h2>Total Change counts by disaster</h2>
                    <Image
                    width="100%"
                    src={`ChangeCounting/summary/charts/${interval.start}_30_${interval.end}_changes_total_count_pie.png`}
                    />
                </div>
            </div>

        </div>
    );
};

