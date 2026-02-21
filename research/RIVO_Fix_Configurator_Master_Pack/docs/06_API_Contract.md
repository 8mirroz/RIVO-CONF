# 6. REST API Contract (черновой)

## POST /api/solutions/generate
Request:
```json
{
  "requirements": {
    "height": 3000,
    "width": 4000,
    "depth": 600,
    "load": 1200,
    "mountingType": "floor-wall"
  }
}
```
Response:
```json
{
  "solutions": [
    {
      "configurationId": "uuid",
      "type": "balanced",
      "structureGraph": {},
      "price": {},
      "bom": [],
      "validationState": {}
    }
  ]
}
```

## POST /api/configuration/validate
## POST /api/cpq/calculate
## POST /api/export/pdf
## POST /api/export/dxf
## POST /api/export/ifc

Примечание: OpenAPI/Swagger генерируется на сервере в /api/docs.

