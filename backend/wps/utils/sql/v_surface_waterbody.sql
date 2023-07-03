CREATE OR REPLACE VIEW public.v_surface_waterbody
AS SELECT
  'SurfaceWaterBody' AS source_table,
  id,
  name,
  geom
FROM
  wps_watercourse
UNION ALL
SELECT
  'WaterCourseNetwork' AS source_table,
  id,
  name,
  geom
FROM
  wps_watercoursenetwork
UNION ALL
SELECT
  'Wetland' AS source_table,
  id,
  name,
  geom
FROM
  wps_wetland;