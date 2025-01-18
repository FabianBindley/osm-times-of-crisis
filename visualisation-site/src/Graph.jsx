import React  from "react";
import "./App.css";
import { Image } from 'antd';

function Graph({ index, graph, graphStyle, interval, periodLength, postOnly, prophetForecast }) {

  // Construct the map path
  const graphPath = `ChangeCounting/disaster${graph.disaster_id}/charts/${interval.start}_${interval.end}_${periodLength}_${graphStyle}${graphStyle=="percent_difference_time_series" & postOnly ? "_post_only" : ""}${graphStyle=="count_changes" & prophetForecast ? "_prophet_forecast" : ""}.png`;
  console.log(graphPath)
  console.log(graphStyle=="count_changes" && prophetForecast ? "_prophet_forecast" : "")
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
