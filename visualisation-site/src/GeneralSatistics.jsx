import React, {useState, useEffect} from 'react';
import "./App.css";
import * as d3 from 'd3-fetch';
import { Image, Select } from 'antd';

export default function GeneralStatistics() {
      const [interval, setInterval] = useState({start:"365", imm:"60", end:"365"})
      const intervalMap = {
        "365-60-365": { start: "365", imm:"60", end: "365" },
        "1095-60-365": { start: "1095", imm:"60", end: "365" },
      };
      const count_change_intervals = [{start:"365", end:"365"},{start:"1095", end:"365"},{start:"180", end:"365"},{start:"90", end:"365"},{start:"90", end:"180"}]
      const [generalStats, setGeneralStats] = useState({})

      const handleIntervalChange = (key) => {
        // Map the key to the corresponding interval object
        setInterval(intervalMap[key]);
      };

      useEffect(() => {
        // Load the data from the CSV file
        const csv_source = `ChangeCounting/summary/data/${interval.start}_${interval.imm}_${interval.end}_full_periods_change_count.csv`
        console.log(csv_source)
        d3.csv(csv_source).then((data) => {
            setGeneralStats(
               data
              );
              console.log(data)
            });
        
      }, []);


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
                        <Select.Option value="1095-365">1095 Pre - 365 Post</Select.Option>
                    </Select>
                </div> 
            </div>
            <p>
            Some general statistics for the selected period:
            </p>
            <div>
                <h2>
                    {generalStats &&
                    <div className='generalStatsText'>
                        <p>
                        <ul>
                            <li>{parseInt(generalStats[3]?.total).toLocaleString()} changes across 16 disasters</li>
                        </ul>
                        </p>
                    </div>
                    }                   
                </h2>
            </div>
            
            <div className="wordcloud-container">
                <div style={{width: '65%'}}>
                    <h2>Changes by period across all disasters</h2>
                    <Image
                    width="100%"
                    src={`ChangeCounting/summary/charts/${interval.start}_60_${interval.end}_changes_count_stacked_bar.png`}
                    />
                </div>
                <div style={{width: '35%'}}>
                    <h2>Total Change counts by disaster</h2>
                    <Image
                    width="100%"
                    src={`ChangeCounting/summary/charts/${interval.start}_60_${interval.end}_changes_total_count_pie.png`}
                    />
                </div>
            </div>

            <div>
                <h2>Area and densities of disasters:</h2>
                <Image
                    width="100%"
                    src={`ChangeDensityMapping/Summary/charts/combined_disaster_area_densities.png`}
                />
                <h2>Percent difference in change density between Pre-Imm and Pre-Post periods:</h2>
                <Image
                    width="90%"
                    src={`ChangeDensityMapping/Summary/charts/percent_difference_density_region.png`}
                />   
                <Image
                    width="90%"
                    src={`ChangeDensityMapping/Summary/charts/percent_difference_density_type.png`}
                />      
            </div>

            <div>
                <h2>Changes to tags across periods</h2>
                <Image
                    width="50%"
                    src={`ChangeDifferences/summary/most_x_key_analysis_365_60_365.png`}
                />
               
            </div>

        </div>
    );
};

