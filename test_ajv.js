const Ajv = require("ajv/dist/2020");
const addFormats = require("ajv-formats");
const fs = require("fs");

const ajv = new Ajv();
addFormats(ajv);
const schema = JSON.parse(fs.readFileSync('contracts/schemas/rivo-config.schema.json', 'utf8'));
const data = JSON.parse(fs.readFileSync('research/RIVO_Deliverables_Passport_DXF_IFC_JSON/05_sample_project.rivo.json', 'utf8'));

const validate = ajv.compile(schema);
const valid = validate(data);

if (!valid) {
  console.log(validate.errors);
  process.exit(1);
} else {
  console.log("Validation successful");
}
