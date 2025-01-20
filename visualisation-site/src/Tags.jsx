import React, { useEffect, useState } from 'react';
import { Select, Switch } from "antd"; 
import TagsDisplayKey from "./TagsDisplayKey";
import TagsDisplayValue from "./TagsDisplayValue";


export default function Tags() {
    const [tagTypeSelection, setTagTypeSelection] = useState(localStorage.getItem("tagTypeSelection") ? localStorage.getItem("tagTypeSelection") : "key")
    const [disasterSelection, setDisasterSelection] = useState("all");
    const [periodSelection, setPeriodSelection] = useState("all");
    const [selectedKey, setSelectedKey] = useState("building");

    const map_areas = [
        "Emilia Romagna Floods | 2023" ,
        "Haiti Earthquake | 2010",
        "Haiti Hurricane Matthew | 2016",
        "Haiti Earthquake and Hurricane | 2021",
        "Nepal Earthquake | 2015",
      ];

    const keys_for_key_values = ["building","highway","source","name","surface","amenity","landuse","waterway","natural"]

    const handleChangePeriodSelection = (key) => {
        setPeriodSelection(key);
      };

      const handleChangeDisasterSelection = (key) => {
        setDisasterSelection(key);
        if (key !== "all") {
            setPeriodSelection("pre")
        }
      };

    const handleChangeTagTypeSelection = (key) => {
        setTagTypeSelection(key);
        localStorage.setItem("tagTypeSelection", key)
      };

      const handleChangeSelectedKey = (key) => {
        setSelectedKey(key);
      };

      const get_word_cloud_source = (disasterSelection, periodSelection,  tagTypeSelection) => {
        
        if (tagTypeSelection=="key")
        {

            if (disasterSelection == "all" & periodSelection=="all")
            {
                return "/TagInvestigation/summary/unique_tag_keys_count_all.csv"
            }
            else if (disasterSelection=="all") {
                return `/TagInvestigation/summary/top_100_keys/${periodSelection}.csv`
            }
            else {
                return `/TagInvestigation/disaster${disasterSelection}/unique_tag_keys_count_${periodSelection}.csv`
            }
        }
        else {
            if (disasterSelection == "all" & periodSelection=="all")
            {
                return "/TagInvestigation/summary/tag_key_values_count_all.csv"
            }
            else if (disasterSelection=="all") {
                return `/TagInvestigation/summary/top_n_tag_key_values/top_100_key_values/${periodSelection}.csv`
            }
            else {
                return `/TagInvestigation/disaster${disasterSelection}/unique_tag_key_values_count_${periodSelection}.csv`
            }
        }


      }

  return (
    <>
        <p>
            Tags were counted for the selected period.
        </p>
        <div className="maps-header">
            <div style={{marginTop:5,marginBottom:5}}>
                    <label style={{ marginLeft: 20 }}>Tag type:</label>
                    <Select
                        value={tagTypeSelection}
                        style={{ width: 150, marginLeft: 10 }}
                        onChange={handleChangeTagTypeSelection}
                    >
                        <Select.Option value="key">Tag keys</Select.Option>
                        <Select.Option value="value">Tag values</Select.Option>
                

                    </Select>
            </div>

            <div style={{marginTop:5,marginBottom:5}}>
                    <label style={{ marginLeft: 20 }}>Disaster:</label>
                    <Select
                        value={disasterSelection}
                        style={{ width: 300, marginLeft: 10 }}
                        onChange={handleChangeDisasterSelection}
                    >
                        <Select.Option value="all">All disasters</Select.Option>
                        {[2, 3, 4, 5, 6].map(num => (
                        <Select.Option key={num} value={num.toString()}>
                            {map_areas[num-2]}
                        </Select.Option>
                        ))}

                    </Select>
            </div>
            
            <div style={{marginTop:5,marginBottom:5}}>
                    <label style={{ marginLeft: 20 }}>Period:</label>
                    <Select
                        value={periodSelection}
                        style={{ width: 150, marginLeft: 10 }}
                        onChange={handleChangePeriodSelection}
                    >
                        {disasterSelection === "all" && <Select.Option value="all">All periods</Select.Option>}
                        <Select.Option value="pre">Pre-disaster</Select.Option>
                        <Select.Option value="imm">Imm-disaster</Select.Option>
                        <Select.Option value="post">Post-disaster</Select.Option>

                    </Select>
            </div>

            {tagTypeSelection == "value" ?
            <div style={{marginTop:5,marginBottom:5}}>
                    <label style={{ marginLeft: 20 }}>Key:</label>
                    <Select
                        value={selectedKey}
                        style={{ width: 150, marginLeft: 10 }}
                        onChange={handleChangeSelectedKey}
                    >
                        {keys_for_key_values.map((key,index) => (
                        <Select.Option key={index} value={key}>
                            {key}
                        </Select.Option>
                        ))}

                    </Select>
            </div> : <div/>}
            
                    
        </div>
        
        <h2>
        The most frequent tag <span style={{fontWeight:'bold'}}>keys</span> in the changes {disasterSelection === "all" ? "across all disasters" : `for ${map_areas[disasterSelection-1]}`}
        </h2>
        {
           tagTypeSelection == "key" ? 
           <TagsDisplayKey csv_source={get_word_cloud_source(disasterSelection, periodSelection, tagTypeSelection)}/> :
           <TagsDisplayValue csv_source={get_word_cloud_source(disasterSelection, periodSelection, tagTypeSelection)} selectedKey={selectedKey}/>
        }
        
    </>
  );
}
