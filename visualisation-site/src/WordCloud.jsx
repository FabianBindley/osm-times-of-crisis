import React, { useEffect, useState } from 'react';
import { Select, Switch } from "antd"; 
import WordCloudDisplay from "./WordCloudDisplay";


export default function WordCloud() {
    const [wordCloudSelection, setWordCloudSelection] = useState("all");
    const [disasterSelection, setDisasterSelection] = useState("all");

    const map_areas = [
        "Broxbourne | 2024",
        "Emilia Romagna Floods | 2023" ,
        "Haiti Earthquake | 2010",
        "Haiti Hurricane Matthew | 2016",
        "Haiti Earthquake and Hurricane Grace | 2021",
        "Nepal Earthquake | 2015",
      ];


    const handleChangeWordCloudSelection = (key) => {
        setWordCloudSelection(key);
      };

      const handleChangeDisasterSelection = (key) => {
        setDisasterSelection(key);
        if (key !== "all") {
            setWordCloudSelection("pre")
        }
      };

      const get_word_cloud_source = (disasterSelection, wordCloudSelection) => {
        
        if (disasterSelection == "all" & wordCloudSelection=="all")
        {
            return "/TagInvestigation/summary/unique_tag_keys_count_all.csv"
        }
        else if (disasterSelection=="all") {
            return `/TagInvestigation/summary/top_100_keys/${wordCloudSelection}.csv`
        }
        else {
            return `/TagInvestigation/disaster${disasterSelection}/unique_tag_keys_count_${wordCloudSelection}.csv`
        }


      }

  return (
    <>
        <p>
            Tags were counted for the selected period.
        </p>
        <div className="maps-header">
            <div style={{marginTop:5,marginBottom:5}}>
                    <label style={{ marginLeft: 20 }}>Disaster:</label>
                    <Select
                        value={disasterSelection}
                        style={{ width: 150, marginLeft: 10 }}
                        onChange={handleChangeDisasterSelection}
                    >
                        <Select.Option value="all">All disasters</Select.Option>
                        {[1, 2, 3, 4, 5, 6].map(num => (
                        <Select.Option key={num} value={num.toString()}>
                            {`Option ${num}`}
                        </Select.Option>
                        ))}

                    </Select>
            </div>
            
            <div style={{marginTop:5,marginBottom:5}}>
                    <label style={{ marginLeft: 20 }}>Period:</label>
                    <Select
                        value={wordCloudSelection}
                        style={{ width: 150, marginLeft: 10 }}
                        onChange={handleChangeWordCloudSelection}
                    >
                        {disasterSelection === "all" && <Select.Option value="all">All periods</Select.Option>}
                        <Select.Option value="pre">Pre-disaster</Select.Option>
                        <Select.Option value="imm">Imm-disaster</Select.Option>
                        <Select.Option value="post">Post-disaster</Select.Option>

                    </Select>
            </div>
            
                    
        </div>
        
        <h2>
        The most frequent tags in the changes {disasterSelection === "all" ? "across all disasters" : `for ${map_areas[disasterSelection-1]}`}
        </h2>

        <WordCloudDisplay csv_source={get_word_cloud_source(disasterSelection, wordCloudSelection)} />
    </>
  );
}
