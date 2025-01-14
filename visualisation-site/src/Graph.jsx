import React  from "react";
import "./App.css";
import { Image } from 'antd';

function Graph({ index, graph, graphStyle, interval, periodLength, postOnly }) {



  // Construct the map path
  const graphPath = `ChangeCounting/disaster${graph.disaster_id}/charts/${interval.start}_${interval.end}_${periodLength}_${graphStyle}${graphStyle=="percent_difference_time_series" & postOnly ? "_post_only" : ""}.png`;
  console.log(graphPath)
  // Render the map or a placeholder
  return (
    <>
      <h2>{graph.title}</h2>
      <div key={index} className="iframe-container">
        <Image
          width="95%"
          src={graphPath}
        />
      </div>

    </>
  );
};

export default Graph;
