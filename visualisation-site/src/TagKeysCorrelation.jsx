import React, { useState, useEffect } from 'react';
import * as d3 from 'd3-fetch';
import { Select, Switch } from "antd"; 

export default function TagKeysCorrelation() {
    const [disasterPeriods, setDisasterPeriods] = useState("pre_imm");
    const [keyCoefficients, setKeyCoefficients] = useState([]);
    const [filterTableByDisasterPeriod, setFilterTableByDisasterPeriod] = useState(localStorage.getItem("filterTableByDisasterPeriod")=="true" ? true : false);

    const csv_source_all = "TagInvestigation/summary/key_correlation_rank_analysis.csv"
    const disasters = [
        { title: "Emilia Romagna Floods | 2023", disaster_id: 2 },
        { title: "Haiti Earthquake | 2010", disaster_id: 3},
        { title: "Haiti Earthquake and Hurricane Grace | 2021", disaster_id: 5},
        { title: "Nepal Earthquake | 2015", disaster_id: 6},
      ];

    const handleChangeDisasterPeriods = (key) => {
        setDisasterPeriods(key);
      };

      const handleChangeFilterTableByDisasterPeriod = () => {
        const result = !filterTableByDisasterPeriod
        setFilterTableByDisasterPeriod(result);
        localStorage.setItem("filterTableByDisasterPeriod", result)
      };


      
        useEffect(() => {
          // Load the data from the CSV file
          console.log(csv_source_all)
          d3.csv(csv_source_all).then((data) => {
            setKeyCoefficients(
              data.filter((d)=> ((`${d.period1}_${d.period2}` === disasterPeriods) || !filterTableByDisasterPeriod) ).map((d) => ({
                disaster: "all",
                period1: d.period1,
                period2: d.period2,
                kendall_rank_correlation: d.kendall_rank_correlation,
                kendall_p_value: d.kendall_p_value,
                cosine_similarity: d.cosine_similarity,
                pearson_correlation: d.pearson_correlation,
                pearson_p_value: d.pearson_p_value,
              }))
            );
          });

          disasters.forEach((disaster) => {
            console.log(disaster);
            d3.csv(`TagInvestigation/disaster${disaster.disaster_id}/key_correlation_rank_analysis.csv`).then((data) => {
              const newCoefficients = data.filter((d)=> ((`${d.period1}_${d.period2}` === disasterPeriods) || !filterTableByDisasterPeriod) ).map((d) => ({
                disaster: disaster.title,
                period1: d.period1,
                period2: d.period2,
                kendall_rank_correlation: d.kendall_rank_correlation,
                kendall_p_value: d.kendall_p_value,
                cosine_similarity: d.cosine_similarity,
                pearson_correlation: d.pearson_correlation,
                pearson_p_value: d.pearson_p_value,
              }));
          
              // Use functional state update to ensure no race conditions
              setKeyCoefficients((prev) => [...prev, ...newCoefficients]);
            });
          });
        }, [disasterPeriods, filterTableByDisasterPeriod]);
    

  return (
    <>
        <p>
            Kendall rank correlation, Pearson correlation, and Cosine similarity coefficients were computed for the selected periods, according to the following keys:
        </p>
        <p>
            Building, highway, source, name, surface, amenity, landuse, waterway, natural
        </p>
        <div className="tag-keys-correlation-container">
            <div className="maps-header">
                <div style={{marginTop:5}}>
                        <label style={{ marginLeft: 20 }}>Periods:</label>
                        <Select
                            value={disasterPeriods}
                            style={{ width: 150, marginLeft: 10 }}
                            onChange={handleChangeDisasterPeriods}
                        >
                            <Select.Option value="pre_imm">Pre - Imm</Select.Option>
                            <Select.Option value="pre_post">Pre - Post</Select.Option>
                            <Select.Option value="imm_post">Imm - Post</Select.Option>

                        </Select>
                </div>

                <div style={{marginTop:5,marginBottom:5}}>
                    <label style={{ marginLeft: 20, marginRight: 10 }}>Filter table by selected period:</label>
                    <Switch checked={filterTableByDisasterPeriod} onChange={handleChangeFilterTableByDisasterPeriod} />
                </div> 
               
            </div>

                <iframe 
                    src={`TagInvestigation/summary/3d_correlation_plot_${disasterPeriods}.html`}
                    title="3D Correlation Plot">
                </iframe>

                {/* Table of all coefficients here */}
                <div style={{ flex: 1, padding: '20px' }}>
                    <h2>Tag key correlation coefficients</h2>
                    <table style={{ width: '100%', borderCollapse: 'collapse', border: '1px solid black' }}>
                    <thead>
                        <tr>
                        <th style={{ border: '1px solid black', padding: '10px' }}>Disaster</th>
                        <th style={{ border: '1px solid black', padding: '10px' }}>Period 1</th>
                        <th style={{ border: '1px solid black', padding: '10px' }}>Period 2</th>
                        <th style={{ border: '1px solid black', padding: '10px' }}>Kendall Rank Correlation</th>
                        <th style={{ border: '1px solid black', padding: '10px' }}>Kendall P-Value</th>
                        <th style={{ border: '1px solid black', padding: '10px' }}>Cosine Similarity</th>
                        <th style={{ border: '1px solid black', padding: '10px' }}>Pearson Correlation Coefficient</th>
                        <th style={{ border: '1px solid black', padding: '10px' }}>Pearson P-Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        {keyCoefficients.map((word, index) => (
                        <tr key={index}>
                            <td style={{ border: '1px solid black', padding: '10px' }}>{word.disaster}</td>
                            <td style={{ border: '1px solid black', padding: '10px' }}>{word.period1}</td>
                            <td style={{ border: '1px solid black', padding: '10px' }}>{word.period2}</td>
                            <td style={{ border: '1px solid black', padding: '10px' }}>{word.kendall_rank_correlation}</td>
                            <td style={{ border: '1px solid black', padding: '10px' }}>{word.kendall_p_value}</td>
                            <td style={{ border: '1px solid black', padding: '10px' }}>{word.cosine_similarity}</td>
                            <td style={{ border: '1px solid black', padding: '10px' }}>{word.pearson_correlation}</td>
                            <td style={{ border: '1px solid black', padding: '10px' }}>{word.pearson_p_value}</td>
                        </tr>
                        ))}
                    </tbody>
                    </table>
                </div>

           

            
        </div>

    </>
  );
}
