import React, { useEffect, useState } from 'react';
import { Select, Switch, InputNumber, Input, Space } from "antd"; 
import TagsDisplayKey from "./TagsDisplayKey";
import TagsDisplayValue from "./TagsDisplayValue";


export default function Tags() {
    const [tagTypeSelection, setTagTypeSelection] = useState(localStorage.getItem("tagTypeSelection") ? localStorage.getItem("tagTypeSelection") : "key")
    const [disasterSelection, setDisasterSelection] = useState("all");
    const [periodSelection, setPeriodSelection] = useState("all");
    const [selectedKey, setSelectedKey] = useState("building");
    const [numTagsShow, setNumTagsShow] = useState(50);
    const [searchTag, setSearchTag] = useState("");

    const { Search } = Input;

    const map_areas = [
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

    const keys_for_key_values = ["building","highway","source","name","surface","amenity","landuse","waterway","natural","leisure","emergency"]

    const handleChangePeriodSelection = (key) => {
        setPeriodSelection(key);
      };

      const handleChangeDisasterSelection = (key) => {
        setDisasterSelection(key);
        if (key !== "all") {
            
        }
      };

    const handleChangeTagTypeSelection = (key) => {
        setTagTypeSelection(key);
        localStorage.setItem("tagTypeSelection", key)
      };

      const handleChangeSelectedKey = (key) => {
        setSelectedKey(key);
      };

      const handleChangeNumTagsShow = (key) => {
        setNumTagsShow(key);
      };

      const handleChangeSearchTag = (e) => {
        setSearchTag(e.target.value);
      };


      const get_word_cloud_source = (disasterSelection, periodSelection,  tagTypeSelection) => {
        
        if (tagTypeSelection=="key")
        {

            if (disasterSelection == "all" & periodSelection=="all")
            {
                return "/TagInvestigation/summary/unique_tag_keys_count_all.csv"
            }
            else if (disasterSelection=="all") {
                return `/TagInvestigation/summary/top_4000_keys/${periodSelection}.csv`
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
                return `/TagInvestigation/summary/top_n_tag_key_values/top_4000_key_values/${periodSelection}.csv`
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
                        {map_areas.map(area => (
                        <Select.Option key={area.disaster_id} value={area.disaster_id.toString()}>
                            {area.title}
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

            <div style={{marginTop:5,marginBottom:5}}>
            <label style={{ marginLeft: 20 }}>Num Tags:</label>
                <InputNumber min={1} max={1000} defaultValue={numTagsShow} onChange={handleChangeNumTagsShow} style={{ marginLeft: 10}} />
            </div>

            <div style={{ marginTop: 5, marginBottom: 5, display: 'flex', alignItems: 'center' }}>
                <label style={{ marginLeft: 20 }}>Search:</label>
                <Search placeholder="input search text" onChange={handleChangeSearchTag} style={{ marginLeft: 10, width: 150 }} />
            </div>
            
                    
        </div>
        
        <h2>
            The most frequent tag <span style={{ fontWeight: 'bold' }}>keys</span> in the changes 
            {disasterSelection === "all"
                ? " across all disasters"
                : ` for ${map_areas.find(area => String(area.disaster_id) === String(disasterSelection))?.title || "Unknown Disaster"}`}
            </h2>

        {
           tagTypeSelection == "key" ? 
           <TagsDisplayKey csv_source={get_word_cloud_source(disasterSelection, periodSelection, tagTypeSelection)} numTagsShow={numTagsShow} searchTag={searchTag} periodSelection={periodSelection}/> :
           <TagsDisplayValue csv_source={get_word_cloud_source(disasterSelection, periodSelection, tagTypeSelection)} selectedKey={selectedKey} numTagsShow={numTagsShow} searchTag={searchTag} periodSelection={periodSelection}/>
        }
        
    </>
  );
}
