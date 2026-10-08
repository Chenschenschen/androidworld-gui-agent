---
name: osmand-plan-route-track
description: Save an OsmAnd track through named waypoints in the listed order. Loaded only for OsmAndTrack.
---
# Saving a track with named waypoints in OsmAnd

Facts about this OsmAnd version (4.6):
- The map opens on a default world view far from the waypoints. Search looks near the map centre: if it shows "Could not find anything", tap INCREASE SEARCH RADIUS, repeating until the place appears. Do not clear or retype the search text in between: that resets the radius. Search for the place name alone (for example "Vaduz"); with ", Liechtenstein" added, only the country is found.
- On a place card, the star button labelled Add saves a Favorite. Favorites are not route points and do not create a track.
- In Plan a route, the Add button adds the point under the centre crosshair. It does not open a search. A point tapped by hand on the map is not exact enough; every waypoint must come from a search result.
- The panel text "points: N" counts the route points. It can update a moment after Add, so check it before tapping Add again. Adding twice at the same centre adds nothing.

Procedure:
1. Launch OsmAnd. Tap the Search (magnifier) button. First type the region named in the task after the comma (the country), tap its result row so the map moves there, and press Back. Then open Search again and type only the first waypoint's place name, for example "Vaduz". Near the map centre it is found without widening the radius.
2. While the search shows "Could not find anything", do not tap SHOW ON MAP and do not zoom: tap INCREASE SEARCH RADIUS until a row with the place name appears. Choose the result that is the place itself (Village, Hamlet or Town), not a guidepost, street, station or shop. If a list of streets inside that place opens, tap the row "SHOW ... ON THE MAP" at the top.
3. On the place card tap Actions, then "Plan a route". The route now shows points: 1.
4. For each next waypoint, in the listed order: in Plan a route tap the Search (magnifier) button, the second round button at the top left (the first, a globe, is Configure map), clear the old text, type the place name and choose the place as in step 2. When its place card is shown, press Back until the Plan a route panel with Add and Done is visible again; the map stays centred on the place. Tap Add and check that "points" increased by one.
5. When "points" equals the number of waypoints, tap Done. The message "GPX file saved to ..." confirms the saved track. Then finish.

If a wrong point was added, use Undo instead of starting again.
