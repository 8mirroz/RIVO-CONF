'use strict';

const fs = require('fs');
const path = require('path');
const { randomUUID } = require('crypto');
const Ajv = require('ajv/dist/2020');
const addFormats = require('ajv-formats');

const ROOT_DIR = path.resolve(__dirname, '../../..');

const DEFAULT_MODEL = {
  attributes: {
    width: { min: 200, max: 3000, step: 10 },
    height: { min: 500, max: 4000, step: 10 },
    depth: { min: 100, max: 1000, step: 10 },
    load: { min: 0, max: 1500 },
    mountingType: ['floor-wall', 'wall', 'floor', 'ceiling'],
    equipmentModules: ['toilet', 'bidet', 'piping', 'sink']
  },
  catalog: {
    profiles: ['profile_30x30', 'profile_40x40']
  },
  rules: {
    hard: [
      {
        id: 'hr1',
        description: 'If load > 400kg, profile MUST be >= 40x40',
        when: { field: 'load', operator: '>', value: 400 },
        action: { type: 'requireProfile', value: 'profile_40x40' },
        explain: 'Heavy loads (>400kg) require a reinforced 40x40 profile.'
      }
    ],
    soft: [
      {
        id: 'sr1',
        description: 'Warn if width > 2000mm',
        when: { field: 'width', operator: '>', value: 2000 },
        explain: "Widths over 2000mm may require additional intermediate supports that aren't auto-added."
      }
    ],
    auto: [
      {
        id: 'ar1',
        description: 'If toilet included, depth must be at least 300mm',
        when: { field: 'equipmentModules', operator: 'contains', value: 'toilet' },
        action: { type: 'setMinOverride', field: 'depth', value: 300 },
        explain: 'Toilet module requires minimum depth 300mm for plumbing clearance.'
      }
    ]
  }
};

let cachedValidators = null;

function maybeReadJson(relativePath) {
  try {
    const fullPath = path.join(ROOT_DIR, relativePath);
    if (!fs.existsSync(fullPath)) return null;
    return JSON.parse(fs.readFileSync(fullPath, 'utf8'));
  } catch {
    return null;
  }
}

function buildValidationModel() {
  return DEFAULT_MODEL;
}

function loadValidators() {
  if (cachedValidators) return cachedValidators;

  const ajv = new Ajv({ allErrors: true, strict: false });
  addFormats(ajv);

  const schemasDir = path.join(ROOT_DIR, 'contracts/schemas');
  if (fs.existsSync(schemasDir)) {
    for (const name of fs.readdirSync(schemasDir)) {
      if (!name.endsWith('.schema.json')) continue;
      const schema = maybeReadJson(path.join('contracts/schemas', name));
      if (schema) ajv.addSchema(schema);
    }
  }

  const configurationSnapshotSchema = maybeReadJson('contracts/schemas/configuration-snapshot.schema.json');
  const validationResultItemSchema = maybeReadJson('contracts/schemas/validation-result-item.schema.json');

  if (!configurationSnapshotSchema || !validationResultItemSchema) {
    throw new Error('Contract schemas for snapshot/validation results are required.');
  }

  const validateSnapshot = ajv.getSchema(configurationSnapshotSchema.$id);
  const validateResultItem = ajv.getSchema(validationResultItemSchema.$id);

  if (!validateSnapshot || !validateResultItem) {
    throw new Error('Failed to initialize contract validators for snapshot/results.');
  }

  cachedValidators = {
    validateSnapshot,
    validateResultItem
  };

  return cachedValidators;
}

function ensureUuid(value) {
  if (typeof value !== 'string') return randomUUID();
  const uuidLike = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidLike.test(value) ? value : randomUUID();
}

function asNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : undefined;
}

function asArray(value) {
  if (Array.isArray(value)) return value;
  if (value === undefined || value === null) return [];
  return [value];
}

function normalizeSnapshotLikeInput(input) {
  const src = input && typeof input === 'object' ? input : {};
  const dimensions = src.dimensions && typeof src.dimensions === 'object' ? src.dimensions : src;

  const normalized = {
    stateId: ensureUuid(src.stateId),
    dimensions: {
      width: asNumber(dimensions.width),
      height: asNumber(dimensions.height),
      depth: asNumber(dimensions.depth)
    }
  };

  if (src.graph && typeof src.graph === 'object') normalized.graph = src.graph;

  if (Array.isArray(src.bom)) {
    normalized.bom = src.bom
      .filter((item) => item && typeof item === 'object')
      .map((item) => {
        const b = {
          article: typeof item.article === 'string' ? item.article : undefined,
          qty: asNumber(item.qty),
          uom: typeof item.uom === 'string' ? item.uom : undefined
        };
        if (typeof item.comment === 'string') b.comment = item.comment;
        return b;
      });
  }

  if (src.versionTag && typeof src.versionTag === 'object') {
    normalized.versionTag = {};
    for (const key of ['catalogVersion', 'rulesVersion', 'pricingVersion', 'assetsVersion']) {
      if (typeof src.versionTag[key] === 'string') normalized.versionTag[key] = src.versionTag[key];
    }
  }

  return normalized;
}

function fromBomProfile(snapshot) {
  if (!Array.isArray(snapshot.bom)) return undefined;
  const found = snapshot.bom.find((i) => typeof i.article === 'string' && i.article.startsWith('profile_'));
  return found ? found.article : undefined;
}

function evaluateCondition(condition, ctx) {
  if (!condition) return false;
  const left = ctx[condition.field];
  const right = condition.value;

  switch (condition.operator) {
    case '>':
      return typeof left === 'number' && left > right;
    case '>=':
      return typeof left === 'number' && left >= right;
    case '<':
      return typeof left === 'number' && left < right;
    case '<=':
      return typeof left === 'number' && left <= right;
    case '==':
      return left === right;
    case '!=':
      return left !== right;
    case 'contains':
      return Array.isArray(left) && left.includes(right);
    default:
      return false;
  }
}

function toResult(payload, validateResultItem) {
  if (validateResultItem(payload)) return payload;
  return {
    ruleId: payload.ruleId || 'internal.result_shape',
    status: 'error',
    message: 'Result payload was sanitized due contract mismatch.',
    explanation: {
      title: 'Internal validation result sanitation',
      message: 'Engine produced an item outside ValidationResultItem schema.',
      why: ['Payload replaced to keep API schema-compatible output.']
    }
  };
}

function schemaErrorsToResults(errors, validateResultItem) {
  if (!Array.isArray(errors)) return [];
  return errors.map((err, i) =>
    toResult(
      {
        ruleId: `schema.${i + 1}`,
        status: 'error',
        message: `${err.instancePath || '/'} ${err.message}`.trim(),
        explanation: {
          title: 'ConfigurationSnapshot schema violation',
          message: 'Input does not match contracts/schemas/configuration-snapshot.schema.json.',
          why: [`Keyword ${err.keyword} failed at ${err.schemaPath}`]
        },
        suggestedFixes: [
          {
            code: 'fix_snapshot_shape',
            message: 'Adjust payload fields/types to match ConfigurationSnapshot contract.'
          }
        ]
      },
      validateResultItem
    )
  );
}

function addNumberRuleResults(results, field, value, rules, validateResultItem) {
  if (typeof value !== 'number') return;

  if (typeof rules.min === 'number' && value < rules.min) {
    results.push(
      toResult(
        {
          ruleId: `attr.${field}.min`,
          status: 'error',
          message: `${field}=${value} is below minimum ${rules.min}`,
          affected: { kind: 'dimension', ids: [field] },
          explanation: {
            title: `${field} below min`,
            message: `${field} must be >= ${rules.min}.`,
            why: ['Value is outside modeled limits.']
          },
          suggestedFixes: [{ code: `set_${field}_${rules.min}`, message: `Set ${field} to at least ${rules.min}` }]
        },
        validateResultItem
      )
    );
  }

  if (typeof rules.max === 'number' && value > rules.max) {
    results.push(
      toResult(
        {
          ruleId: `attr.${field}.max`,
          status: 'error',
          message: `${field}=${value} is above maximum ${rules.max}`,
          affected: { kind: 'dimension', ids: [field] },
          explanation: {
            title: `${field} above max`,
            message: `${field} must be <= ${rules.max}.`,
            why: ['Value is outside modeled limits.']
          },
          suggestedFixes: [{ code: `set_${field}_${rules.max}`, message: `Set ${field} to at most ${rules.max}` }]
        },
        validateResultItem
      )
    );
  }

  if (typeof rules.step === 'number' && typeof rules.min === 'number') {
    const rem = Math.abs((value - rules.min) % rules.step);
    const aligned = rem < 1e-9 || Math.abs(rem - rules.step) < 1e-9;
    if (!aligned) {
      results.push(
        toResult(
          {
            ruleId: `attr.${field}.step`,
            status: 'error',
            message: `${field}=${value} is not aligned with step ${rules.step}`,
            affected: { kind: 'dimension', ids: [field] },
            explanation: {
              title: `${field} step mismatch`,
              message: `${field} must follow increments of ${rules.step} from ${rules.min}.`,
              why: ['Production dimensions use discrete steps.']
            },
            suggestedFixes: [{ code: `snap_${field}_step`, message: `Snap ${field} to nearest valid step` }]
          },
          validateResultItem
        )
      );
    }
  }
}

function validateConfiguration(input, options = {}) {
  const model = buildValidationModel();
  const { validateSnapshot, validateResultItem } = loadValidators();

  const normalizedSnapshot = normalizeSnapshotLikeInput(input);
  const source = input && typeof input === 'object' ? input : {};

  const context = {
    width: normalizedSnapshot.dimensions.width,
    height: normalizedSnapshot.dimensions.height,
    depth: normalizedSnapshot.dimensions.depth,
    load: asNumber(source.load),
    mountingType: source.mountingType,
    equipmentModules: asArray(source.equipmentModules).filter((x) => typeof x === 'string'),
    selectedProfile: source.selectedProfile || source.profileId || fromBomProfile(normalizedSnapshot),
    snapshot: normalizedSnapshot
  };

  const results = [];

  if (!validateSnapshot(normalizedSnapshot)) {
    results.push(...schemaErrorsToResults(validateSnapshot.errors, validateResultItem));
  }

  addNumberRuleResults(results, 'width', context.width, model.attributes.width, validateResultItem);
  addNumberRuleResults(results, 'height', context.height, model.attributes.height, validateResultItem);
  addNumberRuleResults(results, 'depth', context.depth, model.attributes.depth, validateResultItem);
  addNumberRuleResults(results, 'load', context.load, model.attributes.load, validateResultItem);

  if (context.mountingType !== undefined && !model.attributes.mountingType.includes(context.mountingType)) {
    results.push(
      toResult(
        {
          ruleId: 'attr.mountingType.enum',
          status: 'error',
          message: `mountingType=${context.mountingType} is unsupported`,
          affected: { kind: 'attribute', ids: ['mountingType'] },
          explanation: {
            title: 'Unsupported mountingType',
            message: 'mountingType must be one of modeled options.',
            why: ['Invalid mounting type may break constraint interpretation.']
          }
        },
        validateResultItem
      )
    );
  }

  for (const moduleName of context.equipmentModules) {
    if (!model.attributes.equipmentModules.includes(moduleName)) {
      results.push(
        toResult(
          {
            ruleId: 'attr.equipmentModules.enumArray',
            status: 'error',
            message: `equipmentModules contains unsupported option: ${moduleName}`,
            affected: { kind: 'attribute', ids: ['equipmentModules'] },
            explanation: {
              title: 'Unsupported equipment module',
              message: 'All selected modules must be in modeled options.',
              why: ['Unsupported modules have no reliable engineering constraints.']
            }
          },
          validateResultItem
        )
      );
    }
  }

  for (const rule of model.rules.hard) {
    if (!evaluateCondition(rule.when, context)) continue;
    const ok = context.selectedProfile === rule.action.value;

    results.push(
      toResult(
        {
          ruleId: rule.id,
          status: ok ? 'pass' : 'error',
          message: ok
            ? `Required profile ${rule.action.value} is selected.`
            : `${rule.description} (required: ${rule.action.value})`,
          affected: { kind: 'profile', ids: [rule.action.value] },
          explanation: {
            title: rule.description,
            message: rule.explain,
            why: [
              `Condition ${rule.when.field} ${rule.when.operator} ${rule.when.value} is true.`,
              ok ? 'Configuration meets hard rule.' : `Selected profile is ${context.selectedProfile || 'undefined'}.`
            ]
          },
          suggestedFixes: ok
            ? []
            : [{ code: 'select_required_profile', message: `Select ${rule.action.value}` }]
        },
        validateResultItem
      )
    );
  }

  for (const rule of model.rules.soft) {
    const triggered = evaluateCondition(rule.when, context);
    results.push(
      toResult(
        {
          ruleId: rule.id,
          status: triggered ? 'warning' : 'pass',
          message: triggered ? rule.description : `Rule ${rule.id} passed.`,
          explanation: {
            title: rule.description,
            message: rule.explain,
            why: [triggered ? 'Condition is met.' : 'Condition is not met.']
          }
        },
        validateResultItem
      )
    );
  }

  for (const rule of model.rules.auto) {
    if (!evaluateCondition(rule.when, context)) continue;
    const field = rule.action.field;
    const min = rule.action.value;
    const value = context[field];
    const corrected = typeof value === 'number' && value < min;

    results.push(
      toResult(
        {
          ruleId: rule.id,
          status: corrected ? 'auto_corrected' : 'pass',
          message: corrected ? `${field}=${value} below auto minimum ${min}` : `Auto rule ${rule.id} satisfied.`,
          affected: { kind: 'attribute', ids: [field] },
          explanation: {
            title: rule.description,
            message: rule.explain,
            why: [corrected ? `${field} should be raised to ${min}+.` : `${field} already meets minimum ${min}.`]
          },
          suggestedFixes: corrected ? [{ code: `set_${field}_${min}`, message: `Set ${field} to ${min} or higher` }] : []
        },
        validateResultItem
      )
    );
  }

  if (Array.isArray(normalizedSnapshot.bom)) {
    for (const item of normalizedSnapshot.bom) {
      if (item.article && item.article.startsWith('profile_') && !model.catalog.profiles.includes(item.article)) {
        results.push(
          toResult(
            {
              ruleId: 'catalog.profile.exists',
              status: 'error',
              message: `Unknown profile in BOM: ${item.article}`,
              affected: { kind: 'bom', ids: [item.article] },
              explanation: {
                title: 'Unknown catalog profile',
                message: 'BOM profile article is absent in modeled catalog profiles.',
                why: ['Unknown profile cannot be validated for structural safety.']
              }
            },
            validateResultItem
          )
        );
      }
    }
  }

  const includePass = options.includePass !== false;
  return includePass ? results : results.filter((r) => r.status !== 'pass');
}

module.exports = {
  validateConfiguration,
  normalizeSnapshotLikeInput,
  buildValidationModel
};
