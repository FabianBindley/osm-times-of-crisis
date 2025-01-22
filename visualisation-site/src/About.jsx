import React from 'react';
import './About.css'; // Add this CSS file for styling

export default function About() {
  return (
    <div className="about-container">
      <h2 className="about-title">About this Project</h2>
      <p className="about-intro">
        This project investigates crowd-workers' mapping activity on OpenStreetMap (OSM) during times of crisis. 
        By studying natural disasters across different regions and time periods, we aim to understand how 
        contributors respond before, during, and after disasters, and how these responses vary geographically and temporally.
      </p>

      <div className="about-section">
        <h3>Data Sources</h3>
        <p>
          All data used in this project has been sourced from OpenStreetMap (OSM) and downloaded through the&nbsp;
          <a href="https://download.geofabrik.de/" target="_blank" rel="noopener noreferrer" className="about-link">
            Geofabrik
          </a> platform. OSM history data is used, which Geofabrik accesses from the OSM internal server, containing personally identifiable information. 
          All data that may be accessed on <a href="https://osm.fbindley.com/" target="_blank" rel="noopener noreferrer" className="about-link">
            osm.fbindley.com
          </a> is fully aggregated and anonymised: it is not possible to view individual changes and personally identifiable information.
        </p>
      </div>

      <div className="about-section">
        <h3>Included Disasters</h3>
        <p>
          The project focuses on analysing natural disasters from various regions of the world. Below is the list of disasters being studied:
        </p>

        <div className="disaster-list">
          <h4>Americas</h4>
          <ul>
            <li><b>2010 - Haiti Earthquake</b></li>
            <li><b>2017 - Hurricane Harvey (US)</b></li>
            <li><b>2020 - California Wildfires (US)</b></li>
            <li><b>2021 - Haiti Earthquake and Hurricane Grace</b></li>
          </ul>

          <h4>Asia</h4>
          <ul>
            <li><b>2015 - Nepal Earthquake</b></li>
            <li><b>2018 - Indonesia Earthquake</b></li>
            <li><b>2022 - Pakistan Floods</b></li>
            <li><b>2024 - Wayanad Landslide (India)</b></li>
          </ul>

          <h4>Europe and the Middle East</h4>
          <ul>
            <li><b>2020 - Izmir Earthquake (Turkey)</b></li>
            <li><b>2023 - Emilia Romagna Floods (Italy)</b></li>
            <li><b>2023 - Turkey/Syria Earthquake</b></li>
            <li><b>2024 - Valencia Floods (Spain)</b></li>
          </ul>

          <h4>Africa</h4>
          <ul>
            <li><b>2022 - Derna Dam Collapse (Libya)</b></li>
            <li><b>2023 - Cyclone Freddy (Malawi)</b></li>
            <li><b>2023 - Morocco Earthquake</b></li>
          </ul>
        </div>
      </div>

      <div className="about-section">
        <h3>Project Features</h3>
        <p>
          The platform displays information on a number of metrics:
        </p>
        <ul>
          <li><b>Change count variations:</b> how the number of changes users make varies in the pre-disaster, immediate and post-disaster periods,</li>
          <li><b>Change count density mapping:</b> how the spread of changes varies across different areas in the disaster</li>
          <li><b>Tags of changed items: </b>the key,value tags associated with items which users change</li>
        </ul>
      </div>

      <div className="about-section">
        <h3>Ethics</h3>
        <p>
          This project uses publicly available OSM data (although an OSM account is required to access OSM internal history data from Geofabrik), ensuring no personally identifiable information (PII) is included. 
          No individual will be identifiable in this investigation and only aggregate statistics are calculated. 
        </p>
      </div>

      <div className="about-section">
        <h3>Acknowledgments</h3>
        <p>
          We thank the OpenStreetMap community and the Geofabrik platform for providing access to the data used in this analysis. 
            <br/>
          Many libraries have been used to develop this website and its content. These include:
          <h4><b>Research </b></h4>
          <ul>
            <li>Matplotlib</li>
            <li>Pandas</li>
            <li>Postgresql</li>
            <li>PostGIS</li>
            <li>Numpy</li>
            <li>folium</li>
            <li>Osmium</li>
            <li>scipy</li>
            <li>scikit-learn</li>
          </ul>
          <h4><b>Website </b></h4>
          <ul>
            <li>React</li>
            <li>Ant design</li>
            <li>Visx</li>
          </ul>
        </p>
      </div>

      <div className="about-section">
        <h3>Authors</h3>
        <p>
          Fabian Bindley; supervised by Professor Licia Capra
        </p>
      </div>

    </div>

  );
}
