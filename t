                                          List of relations
        Schema         |                       Name                       |    Type     |   Owner    
-----------------------+--------------------------------------------------+-------------+------------
 _timescaledb_cache    | cache_inval_bgw_job                              | table       | postgres
 _timescaledb_cache    | cache_inval_extension                            | table       | postgres
 _timescaledb_cache    | cache_inval_hypertable                           | table       | postgres
 _timescaledb_catalog  | chunk                                            | table       | postgres
 _timescaledb_catalog  | chunk_column_stats                               | table       | postgres
 _timescaledb_catalog  | chunk_constraint                                 | table       | postgres
 _timescaledb_catalog  | chunk_index                                      | table       | postgres
 _timescaledb_catalog  | compression_algorithm                            | table       | postgres
 _timescaledb_catalog  | compression_chunk_size                           | table       | postgres
 _timescaledb_catalog  | compression_settings                             | table       | postgres
 _timescaledb_catalog  | continuous_agg                                   | table       | postgres
 _timescaledb_catalog  | continuous_agg_migrate_plan                      | table       | postgres
 _timescaledb_catalog  | continuous_agg_migrate_plan_step                 | table       | postgres
 _timescaledb_catalog  | continuous_aggs_bucket_function                  | table       | postgres
 _timescaledb_catalog  | continuous_aggs_hypertable_invalidation_log      | table       | postgres
 _timescaledb_catalog  | continuous_aggs_invalidation_threshold           | table       | postgres
 _timescaledb_catalog  | continuous_aggs_materialization_invalidation_log | table       | postgres
 _timescaledb_catalog  | continuous_aggs_watermark                        | table       | postgres
 _timescaledb_catalog  | dimension                                        | table       | postgres
 _timescaledb_catalog  | dimension_slice                                  | table       | postgres
 _timescaledb_catalog  | hypertable                                       | table       | postgres
 _timescaledb_catalog  | metadata                                         | table       | postgres
 _timescaledb_catalog  | tablespace                                       | table       | postgres
 _timescaledb_catalog  | telemetry_event                                  | table       | postgres
 _timescaledb_config   | bgw_job                                          | table       | postgres
 _timescaledb_internal | _compressed_hypertable_4                         | table       | databridge
 _timescaledb_internal | _compressed_hypertable_6                         | table       | loramon
 _timescaledb_internal | _hyper_3_1_chunk                                 | table       | databridge
 _timescaledb_internal | _hyper_3_2_chunk                                 | table       | databridge
 _timescaledb_internal | _hyper_3_3_chunk                                 | table       | databridge
 _timescaledb_internal | _hyper_3_4_chunk                                 | table       | databridge
 _timescaledb_internal | _materialized_hypertable_7                       | table       | loramon
 _timescaledb_internal | _materialized_hypertable_8                       | table       | loramon
 _timescaledb_internal | bgw_job_stat                                     | table       | postgres
 _timescaledb_internal | bgw_job_stat_history                             | table       | postgres
 _timescaledb_internal | bgw_policy_chunk_stats                           | table       | postgres
 app                   | device                                           | table       | loramon
 app                   | floorplan                                        | table       | loramon
 app                   | metric_map                                       | table       | loramon
 app                   | sensor                                           | table       | loramon
 app                   | sensor_placement                                 | table       | loramon
 app                   | sensor_threshold                                 | table       | loramon
 app                   | site                                             | table       | loramon
 app                   | user_account                                     | table       | loramon
 information_schema    | sql_features                                     | table       | postgres
 information_schema    | sql_implementation_info                          | table       | postgres
 information_schema    | sql_parts                                        | table       | postgres
 information_schema    | sql_sizing                                       | table       | postgres
 ingest                | etl_checkpoint                                   | table       | loramon
 ingest                | measurement                                      | table       | loramon
 ingest                | readings                                         | table       | databridge
 pg_catalog            | pg_aggregate                                     | table       | postgres
 pg_catalog            | pg_am                                            | table       | postgres
 pg_catalog            | pg_amop                                          | table       | postgres
 pg_catalog            | pg_amproc                                        | table       | postgres
 pg_catalog            | pg_attrdef                                       | table       | postgres
 pg_catalog            | pg_attribute                                     | table       | postgres
 pg_catalog            | pg_auth_members                                  | table       | postgres
 pg_catalog            | pg_authid                                        | table       | postgres
 pg_catalog            | pg_cast                                          | table       | postgres
 pg_catalog            | pg_class                                         | table       | postgres
 pg_catalog            | pg_collation                                     | table       | postgres
 pg_catalog            | pg_constraint                                    | table       | postgres
 pg_catalog            | pg_conversion                                    | table       | postgres
 pg_catalog            | pg_database                                      | table       | postgres
 pg_catalog            | pg_db_role_setting                               | table       | postgres
 pg_catalog            | pg_default_acl                                   | table       | postgres
 pg_catalog            | pg_depend                                        | table       | postgres
 pg_catalog            | pg_description                                   | table       | postgres
 pg_catalog            | pg_enum                                          | table       | postgres
 pg_catalog            | pg_event_trigger                                 | table       | postgres
 pg_catalog            | pg_extension                                     | table       | postgres
 pg_catalog            | pg_foreign_data_wrapper                          | table       | postgres
 pg_catalog            | pg_foreign_server                                | table       | postgres
 pg_catalog            | pg_foreign_table                                 | table       | postgres
 pg_catalog            | pg_index                                         | table       | postgres
 pg_catalog            | pg_inherits                                      | table       | postgres
 pg_catalog            | pg_init_privs                                    | table       | postgres
 pg_catalog            | pg_language                                      | table       | postgres
 pg_catalog            | pg_largeobject                                   | table       | postgres
 pg_catalog            | pg_largeobject_metadata                          | table       | postgres
 pg_catalog            | pg_namespace                                     | table       | postgres
 pg_catalog            | pg_opclass                                       | table       | postgres
 pg_catalog            | pg_operator                                      | table       | postgres
 pg_catalog            | pg_opfamily                                      | table       | postgres
 pg_catalog            | pg_parameter_acl                                 | table       | postgres
 pg_catalog            | pg_partitioned_table                             | table       | postgres
 pg_catalog            | pg_policy                                        | table       | postgres
 pg_catalog            | pg_proc                                          | table       | postgres
 pg_catalog            | pg_publication                                   | table       | postgres
 pg_catalog            | pg_publication_namespace                         | table       | postgres
 pg_catalog            | pg_publication_rel                               | table       | postgres
 pg_catalog            | pg_range                                         | table       | postgres
 pg_catalog            | pg_replication_origin                            | table       | postgres
 pg_catalog            | pg_rewrite                                       | table       | postgres
 pg_catalog            | pg_seclabel                                      | table       | postgres
 pg_catalog            | pg_sequence                                      | table       | postgres
 pg_catalog            | pg_shdepend                                      | table       | postgres
 pg_catalog            | pg_shdescription                                 | table       | postgres
 pg_catalog            | pg_shseclabel                                    | table       | postgres
 pg_catalog            | pg_statistic                                     | table       | postgres
 pg_catalog            | pg_statistic_ext                                 | table       | postgres
 pg_catalog            | pg_statistic_ext_data                            | table       | postgres
 pg_catalog            | pg_subscription                                  | table       | postgres
 pg_catalog            | pg_subscription_rel                              | table       | postgres
 pg_catalog            | pg_tablespace                                    | table       | postgres
 pg_catalog            | pg_transform                                     | table       | postgres
 pg_catalog            | pg_trigger                                       | table       | postgres
 pg_catalog            | pg_ts_config                                     | table       | postgres
 pg_catalog            | pg_ts_config_map                                 | table       | postgres
 pg_catalog            | pg_ts_dict                                       | table       | postgres
 pg_catalog            | pg_ts_parser                                     | table       | postgres
 pg_catalog            | pg_ts_template                                   | table       | postgres
 pg_catalog            | pg_type                                          | table       | postgres
 pg_catalog            | pg_user_mapping                                  | table       | postgres
 pg_toast              | pg_toast_1213                                    | TOAST table | postgres
 pg_toast              | pg_toast_1247                                    | TOAST table | postgres
 pg_toast              | pg_toast_1255                                    | TOAST table | postgres
 pg_toast              | pg_toast_1260                                    | TOAST table | postgres
 pg_toast              | pg_toast_1262                                    | TOAST table | postgres
 pg_toast              | pg_toast_13375                                   | TOAST table | postgres
 pg_toast              | pg_toast_13380                                   | TOAST table | postgres
 pg_toast              | pg_toast_13385                                   | TOAST table | postgres
 pg_toast              | pg_toast_13390                                   | TOAST table | postgres
 pg_toast              | pg_toast_1417                                    | TOAST table | postgres
 pg_toast              | pg_toast_1418                                    | TOAST table | postgres
 pg_toast              | pg_toast_16565                                   | TOAST table | postgres
 pg_toast              | pg_toast_16595                                   | TOAST table | postgres
 pg_toast              | pg_toast_16620                                   | TOAST table | postgres
 pg_toast              | pg_toast_16627                                   | TOAST table | postgres
 pg_toast              | pg_toast_16660                                   | TOAST table | postgres
 pg_toast              | pg_toast_16706                                   | TOAST table | postgres
 pg_toast              | pg_toast_16713                                   | TOAST table | postgres
 pg_toast              | pg_toast_16740                                   | TOAST table | postgres
 pg_toast              | pg_toast_16749                                   | TOAST table | postgres
 pg_toast              | pg_toast_17173                                   | TOAST table | databridge
 pg_toast              | pg_toast_17234                                   | TOAST table | databridge
 pg_toast              | pg_toast_17247                                   | TOAST table | databridge
 pg_toast              | pg_toast_17260                                   | TOAST table | databridge
 pg_toast              | pg_toast_17276                                   | TOAST table | databridge
 pg_toast              | pg_toast_17353                                   | TOAST table | loramon
 pg_toast              | pg_toast_17368                                   | TOAST table | loramon
 pg_toast              | pg_toast_17394                                   | TOAST table | loramon
 pg_toast              | pg_toast_17425                                   | TOAST table | loramon
 pg_toast              | pg_toast_17470                                   | TOAST table | loramon
 pg_toast              | pg_toast_17482                                   | TOAST table | loramon
 pg_toast              | pg_toast_17492                                   | TOAST table | loramon
 pg_toast              | pg_toast_17507                                   | TOAST table | loramon
 pg_toast              | pg_toast_17522                                   | TOAST table | loramon
 pg_toast              | pg_toast_17555                                   | TOAST table | loramon
 pg_toast              | pg_toast_2328                                    | TOAST table | postgres
 pg_toast              | pg_toast_2396                                    | TOAST table | postgres
 pg_toast              | pg_toast_2600                                    | TOAST table | postgres
 pg_toast              | pg_toast_2604                                    | TOAST table | postgres
 pg_toast              | pg_toast_2606                                    | TOAST table | postgres
 pg_toast              | pg_toast_2609                                    | TOAST table | postgres
 pg_toast              | pg_toast_2612                                    | TOAST table | postgres
 pg_toast              | pg_toast_2615                                    | TOAST table | postgres
 pg_toast              | pg_toast_2618                                    | TOAST table | postgres
 pg_toast              | pg_toast_2619                                    | TOAST table | postgres
 pg_toast              | pg_toast_2620                                    | TOAST table | postgres
 pg_toast              | pg_toast_2964                                    | TOAST table | postgres
 pg_toast              | pg_toast_3079                                    | TOAST table | postgres
 pg_toast              | pg_toast_3118                                    | TOAST table | postgres
 pg_toast              | pg_toast_3256                                    | TOAST table | postgres
 pg_toast              | pg_toast_3350                                    | TOAST table | postgres
 pg_toast              | pg_toast_3381                                    | TOAST table | postgres
 pg_toast              | pg_toast_3394                                    | TOAST table | postgres
 pg_toast              | pg_toast_3429                                    | TOAST table | postgres
 pg_toast              | pg_toast_3456                                    | TOAST table | postgres
 pg_toast              | pg_toast_3466                                    | TOAST table | postgres
 pg_toast              | pg_toast_3592                                    | TOAST table | postgres
 pg_toast              | pg_toast_3596                                    | TOAST table | postgres
 pg_toast              | pg_toast_3600                                    | TOAST table | postgres
 pg_toast              | pg_toast_6000                                    | TOAST table | postgres
 pg_toast              | pg_toast_6100                                    | TOAST table | postgres
 pg_toast              | pg_toast_6106                                    | TOAST table | postgres
 pg_toast              | pg_toast_6243                                    | TOAST table | postgres
 pg_toast              | pg_toast_826                                     | TOAST table | postgres
(179 rows)

