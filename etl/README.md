# ETL

Script que converte registros de `raw.uplink` em pontos na tabela `ingest.measurement`.

## `json_path`

Cada linha de `app.metric_map` define `metric` e um `json_path` que aponta
para o valor dentro do payload JSON. O caminho é separado por vírgulas e
suporta índices de arrays utilizando números. Exemplos:

- `{object,internal_sensors_temperature}`
- `{rxInfo,0,rssi}`  – acessa o primeiro elemento do array `rxInfo` e o campo `rssi`.

Se `label` não for informado na `metric_map`, o nome da própria métrica será
usado como `sensor_id` na inserção.

## Dry-run

Para diagnosticar mapeamentos execute:

```bash
python etl.py --once --limit 20 --verbose
```

O comando acima busca os últimos 20 uplinks e imprime uma tabela com
`metric -> json_path -> valor` (ou `MISSING`). Nenhum dado é gravado no banco.
