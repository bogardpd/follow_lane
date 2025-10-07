# follow_lane
Traces individual road lanes in GeoPackage data.

## Usage

### follow_lane

Takes a network of lanes and determines if any of them loop back to the same road segment (either in the same lane or a different lane).

#### Usage

`python follow_lane.py`

Options

- `--source SOURCE` (required) GeoPackage source path.
- `--output OUTPUT [OUTPUT ...]` (optional) GraphML output file.
- `--paint` If present, allows starting or ending lanes to cross dotted paint lines.

Using data source roads.gpkg, find segment loops and export to roads.graphml:

`python follow_lane.py --source roads.gpkg --output roads.graphml`

## Lanes

For this project, a lane is defined as a continuous stretch of road between two painted lines (which may be solid or dashed).

If two adjacent lanes merge into one without either movement crossing a solid or dashed paint line, the lane follower follows both of them into the new lane. Likewise, if a lane splits into two without either movement crossing a solid or dashed paint line, the lane follower will follow both branches. (If the `--paint` flag is set, the lane follower will follow a lane merge or split even if it crosses a paint line.)

## GeoPackage Format

The source argument must point to a GeoPackage file with the following layers:

### road_segments (LineString, WGS&nbsp;84)

Geometry of road segments (where each segment contains a consistent number of lanes). Additional fields are acceptable but ignored. Geometry should use the WGS&nbsp;84 ellipsoid.

### connectors (No Geometry)

A table documenting the interaction of lanes between road segments, with the following format:

| Field | Type | Description |
|-------|------|-------------|
| fid   | int64 | Connection feature ID |
| from_segment_fid | int64 | The segment a lane is coming from (in the direction of travel) |
| from_lane_number | int64 | The lane number within the segment the lane is coming from. See [Lane Numbering](#lane-numbering) below. |
| to_segment_fid | int64 | The segment a lane is going to (in the direction of travel) |
| to_lane_number | int64 | The lane number within the segment the lane is going to. See [Lane Numbering](#lane-numbering) below. |
| crosses_paint | bool | If a lane begins or ends in such a way that a driver can't enter it (new lanes) or exit it (ending lanes) without crossing a paint line, this should be set to true. Otherwise, false. |

In most cases, lanes will line up (lane 0 in segment n will connect to lane 0 in segment n + 1). However, this can also be used to document lanes splitting (lane 0 could go to two different lanes in the same segment, or a different lane in two different segments) or merging (two different lanes in the same segment become connect to a single lane in the following segment, or lanes from two different segments connect to a single lane in another segment). Each lane connection will have its own row.

## Lane Numbering

![Diagram showing lane numbering](/images/lane_numbering.png)

Lane numbering is based on the lane’s direction of travel relative to the direction of the LineString geometry. Lanes which travel in the direction of the LineString are _forward_ lanes, and lanes which travel opposite to the LineString are _reverse_ lanes.

For regions that drive on the right, forward lanes are numbered starting with 0 for the leftmost lane and increasing from there (0, 1, 2…). Reverse lanes are numbered starting with −1 for the leftmost lane and decreasing from there (−1, −2, −3…)

For regions that drive on the left, numbering starts with the rightmost lane in each direction, but otherwise follows the same rules.
