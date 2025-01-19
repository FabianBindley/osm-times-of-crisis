import React, { useState } from 'react';
import { Select, Switch } from "antd"; 
export default function TagKeysCorrelation() {
    const [disasterPeriods, setDisasterPeriods] = useState("pre_imm");
    const handleChangeDisasterPeriods = (key) => {
        setDisasterPeriods(key);
      };
    

  return (
    <>
        <p>
            Kendall rank correlation, Pearson correlation, and Cosine similarity coefficients were computed for the selected periods, according to the following keys:
        </p>
        <p>
            Building, highway, name, surface, amenity, landuse, waterway, natural
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
               
            </div>
            
                <iframe 
                    src={`TagInvestigation/summary/3d_correlation_plot_${disasterPeriods}.html`}
                    title="3D Correlation Plot">
                </iframe>
           

            
        </div>

    </>
  );
}
