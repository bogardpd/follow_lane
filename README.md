# follow_lane
Traces individual road lanes in OpenStreetMap data.

> [!NOTE]
> This project is in progress, and significant functionality has not yet been implemented.

## Setup

This project requires [Osmium Tool](https://osmcode.org/osmium-tool/) to be available at the command line. On Windows, this can be installed under WSL; just be sure to also run the Python scripts from WSL.

This project requires downloaded OpenStreetMap data in PBF (.osm.pbf) format. One source for this at the continent, country, or region level is [https://download.geofabrik.de/](https://download.geofabrik.de/).

Since this data can be large for any sizable region, consider filtering it to only include roads:

`osmium tags-filter us-latest.osm.pbf nwr/highway -o us-roads.osm.pbf`

You can also specify a bounding box:

`osmium extract us-roads.osm.pbf -b -78.7,38.4,-76.4,39.5 -o dc-roads.osm.pbf`

## Usage

Using data source dc-roads.osm.pbf, follow the lane starting with OSM way 5973741:

`python follow_lane.py --pbf dc-roads.osm.pbf --way 5973741`