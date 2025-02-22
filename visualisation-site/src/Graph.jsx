import React  from "react";
import "./App.css";
import { Image } from 'antd';

function Graph({ index, graph, graphStyle, interval, periodLength, postOnly, prophetForecast, edit_type, disasterIdsSortType }) {
  let graphPath;
  // Construct the map path
  if (graphStyle === "counts")
  {
    graphPath = `ChangeCounting/${graph.disaster_id == 0 ? "combined" : `disaster${graph.disaster_id}`}/charts/${interval.start}_${interval.imm}_${interval.end}_${periodLength}_${graphStyle}${prophetForecast ? "_prophet_forecast" : ""}${edit_type =="all" ? "" : "_"+edit_type}${postOnly ? "_post_only" : ""}${graph.disaster_id == 0 ? "_grid_"+disasterIdsSortType : ""}.png`;
  }
  else if(graphStyle === "percent_difference_time_series") {
    graphPath = `ChangeCounting/disaster${graph.disaster_id}/charts/${interval.start}_${interval.imm}_${interval.end}_${periodLength}_${graphStyle}${edit_type =="all" ? "" : "_"+edit_type}${postOnly ? "_post_only" : ""}.png`;
  }
  else if (graphStyle === "avg_days_between_edits") {
    graphPath = `ChangeDifferences/${graph.disaster_id == 0 ? "combined" : `disaster${graph.disaster_id}`}/days_between_edits/charts/${interval.start}_${interval.imm}_${interval.end}_${periodLength === "day" ? "1" : periodLength === "week" ? "7" :"30"}_${graphStyle}${prophetForecast ? "_prophet_forecast" : ""}${postOnly ? "_post_only" : ""}${graph.disaster_id == 0 ? "_grid_"+disasterIdsSortType : ""}.png`;
  }
  else {
        graphPath = `ChangeDifferences/${graph.disaster_id == 0 ? "combined" : `disaster${graph.disaster_id}`}/tag_changes/charts/${interval.start}_${interval.imm}_${interval.end}_${periodLength}_${graphStyle}${prophetForecast ? "_prophet_forecast" : ""}${edit_type =="all" ? "" : "_"+edit_type}${postOnly ? "_post_only" : ""}${graph.disaster_id == 0 ? "_grid_"+disasterIdsSortType : ""}.png`;
  }
  
  console.log(graphPath)
  // Render the map or a placeholder
  return (
    <>
      <h2>{graph.title}</h2>
      <div key={index} className="iframe-container-normal">
        <Image
          width="85%"
          src={graphPath}
        />
      </div>

    </>
  );
};

export default Graph;
