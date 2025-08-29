-- Rename device_prof to device_profile and add enabled flag to metric_map
ALTER TABLE app.metric_map
  RENAME COLUMN device_prof TO device_profile;

ALTER TABLE app.metric_map
  ADD COLUMN enabled boolean NOT NULL DEFAULT true;

