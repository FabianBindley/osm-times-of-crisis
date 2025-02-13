import React, { useState, useEffect } from "react";
import "./App.css";
import * as d3 from "d3-fetch";
import { Select, Image, Spin } from "antd";

export default function TagUsageCharts() {
  const [tagTypeSelection, setTagTypeSelection] = useState(
    localStorage.getItem("tagTypeSelection") || "key"
  );
  const [selectedKey, setSelectedKey] = useState("");
  const [tagKeysTopValues, setTagKeysTopValues] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load JSON file correctly
    const json_source = `TagInvestigation/summary/tag_keys_top_values.json`;
    console.log("Fetching:", json_source);

    d3.json(json_source)
      .then((data) => {
        setTagKeysTopValues(data);
        console.log("Loaded data:", data);

        // Set first key as default if data exists
        const firstKey = Object.keys(data)[0] || "";
        setSelectedKey(firstKey);
      })
      .catch((error) => console.error("Error loading JSON:", error))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="maps-header">
        {/* Tag Type Selector */}
        <div style={{ marginTop: 5, marginBottom: 5 }}>
          <label style={{ marginLeft: 20 }}>Tag type:</label>
          <Select
            value={tagTypeSelection}
            style={{ width: 150, marginLeft: 10 }}
            onChange={(key) => {
              setTagTypeSelection(key);
              localStorage.setItem("tagTypeSelection", key);
            }}
          >
            <Select.Option value="key">Tag keys</Select.Option>
            <Select.Option value="value">Tag values</Select.Option>
          </Select>
        </div>

        {/* Key Selector when 'value' is selected */}
        {tagTypeSelection === "value" && (
          <div style={{ marginTop: 5, marginBottom: 5 }}>
            <label style={{ marginLeft: 20 }}>Key:</label>
            <Select
              value={selectedKey}
              style={{ width: 150, marginLeft: 10 }}
              onChange={setSelectedKey}
            >
              {Object.keys(tagKeysTopValues).map((key) => (
                <Select.Option key={key} value={key}>
                  {key}
                </Select.Option>
              ))}
            </Select>
          </div>
        )}
      </div>

      <p>Tag usage charts</p>

      {/* Show loading spinner while fetching data */}
      {loading && <Spin size="large" style={{ display: "block", margin: "auto" }} />}

      {tagTypeSelection === "key" && (
            <>
                <h3>Usage charts for features:</h3>
                {Object.keys(tagKeysTopValues).map((key) => (
                <div key={key} className="chart">
                    <h3>{key}</h3>
                    <Image
                    width="80%"
                    src={`TagInvestigation/summary/charts/key_usage_charts/usage_${key}.png`} 
                    alt={`Usage chart for ${key}`}
                    />
                </div>
                ))}
            </>
            )}


      {tagTypeSelection === "value" && selectedKey && tagKeysTopValues[selectedKey] && (
        <>
          <h3>Usage charts of objects of feature type: '{selectedKey}'</h3>
          <div className="charts-container">
            {Array.isArray(tagKeysTopValues[selectedKey]) &&
              tagKeysTopValues[selectedKey].map((value) => (
                <div key={value} className="chart">
                <h3>{value}</h3>
                  <Image
                    width="80%"
                    src={`TagInvestigation/summary/charts/key_value_usage_charts/usage_${selectedKey}_${value}.png`} 
                    alt={`Usage chart for ${selectedKey} - ${value}`}
                  />
                </div>
              ))}
          </div>
        </>
      )}
    </div>
  );
}
