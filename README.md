# follow_lane
Traces individual road lanes in GeoPackage data.

> [!NOTE]
> This project is in progress, and significant functionality has not yet been implemented.

## Usage

### follow_lane

Accepts a starting road segment and lane number and follows the specified lane through its branches.

#### Usage

`python follow_lane.py`

Options

- `--source SOURCE` (required) GeoPackage source path
- `--start fid lane` (optional) Starts following from the node with the specified fid and lane number (zero-indexed)
- `--output OUTPUT [OUTPUT ...]` (optional) Output file(s). Supports **.graphml**.

Using data source roads.gpkg, follow the leftmost lane of feature 12345 and export to roads.graphml:

`python follow_lane.py --source roads.gpkg --start 12345 0 --output roads.graphml`

## GeoPackage Format

The source argument must point to a GeoPackage file with the following layers:

### road_segments (LineString)

Geometry of road segments (where each segment contains a consistent number of lanes). Additional fields are acceptable but ignored.

### connectors (No Geometry)

A table documenting the interaction of lanes between road segments, with the following format:

| Field | Type | Description |
|-------|------|-------------|
| fid   | int64 | Connection feature ID |
| from_segment_fid | int64 | The segment a lane is coming from (in the direction of travel) |
| from_lane_number | int64 | The lane number within the segment the lane is coming from. Zero-indexed, starting with the leftmost lane in the direction of travel (so the far left lane is `0`).
| to_segment_id | int64 | The segment a lane is going to (in the direction of travel) |
| to_lane_number | int64 | The lane number within the segment the lane is going to. Zero-indexed, starting with the leftmost lane in the direction of travel (so the far left lane is `0`).
| crosses_paint | bool | If a lane begins or ends in such a way that a driver can't enter it (new lanes) or exit it (ending lanes) without crossing a paint line, this should be set to true. Otherwise, false. |

In most cases, lanes will line up (lane 0 in segment n will connect to lane 0 in segment n + 1). However, this can also be used to document lanes splitting (lane 0 could go to two different lanes in the same segment, or a different lane in two different segments) or merging (two different lanes in the same segment become connect to a single lane in the following segment, or lanes from two different segments connect to a single lane in another segment). Each lane connection will have its own row.
