import React, { useEffect, useState } from 'react';
import { Wordcloud } from '@visx/wordcloud';
import * as d3 from 'd3-fetch';
import { scaleLinear } from 'd3-scale';
import { interpolateHcl } from 'd3-interpolate';

// Define font size and rotation mappers
const fontSizeMapper = (word) => Math.log2(word.value) * 3;
const rotationMapper = () => Math.random() * 10 - 5;

// Define a color scale based on frequency
const colorScale = (value, maxValue) => {
  const scale = scaleLinear()
    .domain([0, maxValue]) // Map value range (0 to maxValue)
    .range(['#00FF00', '#FF000F']) // Color range (light to dark)
    .interpolate(interpolateHcl); // Smooth color interpolation
  return scale(value);
};

export default function TagsDisplay({csv_source, numTagsShow, searchTag, periodSelection}) {
  const [words, setWords] = useState([]);

  useEffect(() => {
    // Load the data from the CSV file
    console.log(csv_source)
    d3.csv(csv_source).then((data) => {
      setWords(
        data.map((d) => ({
          text: d.key,
          value: +d.count,
          percent_of_total_changes: +d.percent_of_total_changes,
          percent_difference_from_pre: +d.percent_difference_from_pre,
          percent_difference_from_pre_day: +d.percent_difference_from_pre_day,
        })).filter((d) => d.text.includes(searchTag.toLowerCase()))
           .slice(0, numTagsShow)
      );
    });
  }, [csv_source, numTagsShow, searchTag, periodSelection]);

  return (
    <>
     <div className="wordcloud-container">
        <div style={{ display: 'flex', flexDirection: 'row' }}>
        {/* Wordcloud on the left */}
        <div style={{ flex: 1, padding: '20px' }}>
            <h2>Word Cloud</h2>
            <Wordcloud
            words={words}
            fontSize={fontSizeMapper}
            rotate={rotationMapper}
            padding={5}
            width={600}
            height={400}
            children={(cloudWords) => {
                const maxValue = Math.max(...words.map((w) => w.value)); // Get the maximum value
                return cloudWords.map((word, index) => (
                <text
                    key={index}
                    fontSize={word.size}
                    textAnchor="middle"
                    transform={`translate(${word.x}, ${word.y}) rotate(${word.rotate})`}
                    style={{ fill: colorScale(word.value, maxValue),
                        fontFamily: "'Oswald', sans-serif", // Apply Oswald font
                        fontWeight: 'bold', // Make it bold
                     }} // Map color based on frequency
                >
                    {word.text}
                </text>
              
                ));
            }}
            />
        </div>

        <div style={{ flex: 1, padding: '20px' }}>
            <h2>Key Details</h2>
            <table style={{ width: '100%', borderCollapse: 'collapse', border: '1px solid black' }}>
            <thead>
                <tr>
                <th style={{ border: '1px solid black', padding: '10px' }}>Index</th>
                <th style={{ border: '1px solid black', padding: '10px' }}>Key</th>
                <th style={{ border: '1px solid black', padding: '10px' }}>Count</th>
                <th style={{ border: '1px solid black', padding: '10px' }}>% of Total Changes For Period</th>
                {(periodSelection == "imm" || periodSelection == "post") && 
                  <>
                  <th style={{ border: '1px solid black', padding: '10px',  maxWidth: '200px', wordWrap: 'break-word'}}>% difference from pre-disaster</th>
                  
                  {periodSelection == "imm" &&
                  <th style={{ border: '1px solid black', padding: '10px',  maxWidth: '200px', wordWrap: 'break-word'}}>% difference from pre-disaster per day</th>
                  }
                  </>
                }
                </tr>
            </thead>
            <tbody>
                {words.map((word, index) => (
                <tr key={index}>
                    <td style={{ border: '1px solid black', padding: '10px' }}>{index}</td>
                    <td style={{ border: '1px solid black', padding: '10px' }}>{word.text}</td>
                    <td style={{ border: '1px solid black', padding: '10px' }}>{word.value}</td>
                    <td style={{ border: '1px solid black', padding: '10px' }}>
                    {word.percent_of_total_changes.toFixed(3)}%
                    </td>
                    {(periodSelection == "imm" || periodSelection == "post") && 
                    <>
                      <td style={{ border: '1px solid black', padding: '10px' }}>
                      {word.percent_difference_from_pre.toFixed(3)}%
                      </td>
                      {periodSelection == "imm" &&
                            <td style={{ border: '1px solid black', padding: '10px' }}>
                        {word.percent_difference_from_pre_day.toFixed(3)}%
                        </td>
                      }
                     
                    </>

                    }
                </tr>
                ))}
            </tbody>
            </table>
          </div>
        </div>
        </div>
    </>
  );
}
