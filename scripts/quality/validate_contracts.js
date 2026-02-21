const fs = require('fs');
const path = require('path');
const Ajv = require('ajv/dist/2020');
const addFormats = require('ajv-formats');

const ajv = new Ajv({ allErrors: true });
addFormats(ajv);

const schemaDir = path.join(__dirname, '..', '..', 'contracts', 'schemas');
const examplesDir = path.join(__dirname, '..', '..', 'contracts', 'examples');

function loadJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

// Load all schemas
const schemaFiles = fs.readdirSync(schemaDir).filter(f => f.endsWith('.json'));
for (const f of schemaFiles) {
  const schema = loadJson(path.join(schemaDir, f));
  ajv.addSchema(schema, schema.$id || f);
}

const exampleMap = {
  'example.snapshot.json': 'https://rivo.example/schema/configuration-snapshot.schema.json',
  'example.validation.json': 'https://rivo.example/schema/validation-result-item.schema.json',
  'example.pricequote.json': 'https://rivo.example/schema/price-quote.schema.json',
  'example.bom.json': 'https://rivo.example/schema/bom-item.schema.json',
  'example.export.rivo.json': 'https://rivo.example/schema/rivo-config.schema.json'
};

let ok = true;
for (const [exampleFile, schemaId] of Object.entries(exampleMap)) {
  const examplePath = path.join(examplesDir, exampleFile);
  const data = loadJson(examplePath);
  const validate = ajv.getSchema(schemaId);
  if (!validate) {
    ok = false;
    console.error(`Missing schema: ${schemaId}`);
    continue;
  }

  const validateOne = (item, idx) => {
    const valid = validate(item);
    if (!valid) {
      ok = false;
      const suffix = typeof idx === 'number' ? `[${idx}]` : '';
      console.error(`Validation failed for ${exampleFile}${suffix}`);
      console.error(validate.errors);
    }
  };

  if (Array.isArray(data)) {
    data.forEach((item, idx) => validateOne(item, idx));
  } else {
    validateOne(data, undefined);
  }

  if (ok) console.log(`OK: ${exampleFile}`);
}

if (!ok) process.exit(1);
