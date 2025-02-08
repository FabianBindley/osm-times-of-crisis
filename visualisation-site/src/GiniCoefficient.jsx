import React, {useState} from 'react';
import "./App.css";
import { Image, Select, Switch } from 'antd';

export default function GiniCoefficient() {
    
    const [resolution, setResolution] = useState("7")
    const [totalOnly, setTotalOnly] = useState(localStorage.getItem("totalOnly")=="true" ? true : false);
      
      const handleResolutionChange = (value) => {
        setResolution(value);
    };

    const handleChangeTotalOnly = (checked) => {
        setTotalOnly(checked)
        localStorage.setItem("totalOnly", checked)
    }

    return (
        <div>
            <div className="maps-header">
                <div style={{marginTop:5,marginBottom:5}}>
                    <label style={{ marginLeft: 10 }}>Resolution:</label>
                    <Select
                        defaultValue={resolution}
                        value={resolution}
                        style={{ width: 60, marginLeft: 10 }}
                        onChange={handleResolutionChange}
                    >
                        <Select.Option value="7">7</Select.Option>
                        <Select.Option value="8">8</Select.Option>
                        <Select.Option value="9">9</Select.Option>
                    </Select>
                </div> 

                <div style={{marginTop:5,marginBottom:5}}>
                    <label style={{ marginLeft: 20, marginRight: 10 }}>Total only:</label>
                    <Switch checked={totalOnly} onChange={handleChangeTotalOnly} />
                </div> 

            </div>


            <p>
                The following gini coefficient % differences were computed by calculating the difference between the number of changes of each type in each hexagon cell, in the pre, and imm/post disaster periods. 
                <br/>
                An increase means that counts are more unequal and concentrated, while a decrease means that changes are more spread out. 
                <br/>
                Atami had no hexagon in resolution 7, therefore its counts are 0
            </p>

        
                    <h2>Changes by period across all disasters</h2>
                    <Image
                    width="80%"
                    src={`ChangeDensityMapping/Summary/charts/gini_percent_difference_${resolution}_${totalOnly ? "total_only" : ""}.png`}
                    />
          

        </div>
    );
};

