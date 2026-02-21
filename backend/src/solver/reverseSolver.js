'use strict';

const { randomUUID } = require('crypto');
const { validateConfiguration, normalizeSnapshotLikeInput, buildValidationModel } = require('../validation');

function asNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : undefined;
}

function unique(values) {
  return [...new Set(values)];
}

function snapToStep(value, min, step) {
  if (!Number.isFinite(value) || !Number.isFinite(min) || !Number.isFinite(step) || step <= 0) return value;
  const snapped = min + Math.round((value - min) / step) * step;
  return Number(snapped.toFixed(6));
}

function dimCandidates(target, rules, breadth = 2) {
  const min = Number.isFinite(rules.min) ? rules.min : 0;
  const max = Number.isFinite(rules.max) ? rules.max : min + 1000;
  const step = Number.isFinite(rules.step) ? rules.step : 10;
  const fallback = min + (max - min) / 2;
  const wanted = Number.isFinite(target) ? target : fallback;
  const center = snapToStep(wanted, min, step);

  const raw = [center, min, max];
  for (let i = 1; i <= breadth; i += 1) {
    raw.push(center + i * step, center - i * step);
  }

  return unique(raw)
    .map((v) => Math.max(min, Math.min(max, snapToStep(v, min, step))))
    .sort((a, b) => Math.abs(a - wanted) - Math.abs(b - wanted));
}

function buildCandidateInput(target, dims, profileId) {
  return {
    stateId: randomUUID(),
    dimensions: dims,
    load: target.load,
    mountingType: target.mountingType,
    equipmentModules: target.equipmentModules,
    selectedProfile: profileId,
    bom: profileId
      ? [{ article: profileId, qty: 1, uom: 'pcs', comment: 'candidate profile' }]
      : []
  };
}

function candidateScore(candidate, target) {
  const d = candidate.snapshot.dimensions;
  let score = 0;

  if (target.width !== undefined) score += Math.abs((d.width ?? 0) - target.width);
  if (target.height !== undefined) score += Math.abs((d.height ?? 0) - target.height);
  if (target.depth !== undefined) score += Math.abs((d.depth ?? 0) - target.depth);

  for (const item of candidate.validation) {
    if (item.status === 'error') score += 100000;
    if (item.status === 'warning') score += 300;
    if (item.status === 'auto_corrected') score += 150;
  }

  if (target.selectedProfile && candidate.profileId !== target.selectedProfile) {
    score += 500;
  }

  return score;
}

function isExact(candidate, target) {
  if (candidate.validation.some((x) => x.status !== 'pass')) return false;

  const d = candidate.snapshot.dimensions;
  if (target.width !== undefined && d.width !== target.width) return false;
  if (target.height !== undefined && d.height !== target.height) return false;
  if (target.depth !== undefined && d.depth !== target.depth) return false;
  if (target.selectedProfile && candidate.profileId !== target.selectedProfile) return false;

  return true;
}

function relaxationHints(target, candidates) {
  const hints = [];
  const has = (ruleId) => candidates.some((c) => c.validation.some((v) => v.ruleId === ruleId));

  if (has('hr1')) {
    hints.push({
      code: 'select_profile_40x40',
      message: 'For load > 400kg select profile_40x40.'
    });
  }

  if (has('ar1')) {
    hints.push({
      code: 'raise_depth_for_toilet',
      message: 'When toilet is selected, increase depth to 300mm or more.'
    });
  }

  if (target.width !== undefined) {
    hints.push({
      code: 'relax_width_step',
      message: 'Try nearest width value aligned to 10mm step.'
    });
  }

  if (!hints.length) {
    hints.push({
      code: 'relax_primary_dimensions',
      message: 'Relax primary dimensions by one production step and retry.'
    });
  }

  return hints;
}

function solveReverse(targetParams = {}, options = {}) {
  const model = buildValidationModel();

  const target = {
    width: asNumber(targetParams.width),
    height: asNumber(targetParams.height),
    depth: asNumber(targetParams.depth),
    load: asNumber(targetParams.load),
    mountingType: targetParams.mountingType,
    equipmentModules: Array.isArray(targetParams.equipmentModules) ? targetParams.equipmentModules : [],
    selectedProfile: targetParams.selectedProfile || targetParams.profileId
  };

  const widthValues = dimCandidates(target.width, model.attributes.width, options.dimensionBreadth || 2);
  const heightValues = dimCandidates(target.height, model.attributes.height, options.dimensionBreadth || 2);
  const depthValues = dimCandidates(target.depth, model.attributes.depth, options.dimensionBreadth || 2);
  const profiles = target.selectedProfile ? [target.selectedProfile] : model.catalog.profiles;

  const maxCandidates = Number.isFinite(options.maxCandidates) ? options.maxCandidates : 200;
  const maxSolutions = Number.isFinite(options.maxSolutions) ? options.maxSolutions : 10;

  const evaluated = [];

  outer: for (const width of widthValues) {
    for (const height of heightValues) {
      for (const depth of depthValues) {
        for (const profileId of profiles) {
          const input = buildCandidateInput(target, { width, height, depth }, profileId);
          const validation = validateConfiguration(input, { includePass: true });
          const snapshot = normalizeSnapshotLikeInput(input);

          const candidate = {
            profileId,
            snapshot,
            validation
          };

          candidate.score = candidateScore(candidate, target);
          evaluated.push(candidate);

          if (evaluated.length >= maxCandidates) break outer;
        }
      }
    }
  }

  evaluated.sort((a, b) => a.score - b.score);

  const valid = evaluated.filter((c) => !c.validation.some((x) => x.status === 'error'));
  const exactMatch = valid.some((c) => isExact(c, target));

  const solutions = valid.slice(0, maxSolutions).map((c, i) => ({
    rank: i + 1,
    score: c.score,
    profileId: c.profileId,
    snapshot: c.snapshot,
    validation: c.validation.filter((v) => v.status !== 'pass')
  }));

  return {
    exactMatch,
    evaluatedCandidates: evaluated.length,
    solutions,
    relaxationHints: exactMatch ? [] : relaxationHints(target, evaluated)
  };
}

module.exports = {
  solveReverse,
  dimCandidates
};
