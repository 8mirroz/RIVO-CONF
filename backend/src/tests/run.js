'use strict';
/**
 * P1-05: Regression suite for rules and solver.
 * Runs standalone - no test framework required.
 */
const assert = require('assert');
const { validateConfiguration } = require('../validation/validationEngine');
const { solveReverse } = require('../solver/reverseSolver');
const { calculateCpq } = require('../cpq/cpqEngine');

let passed = 0;
let failed = 0;

function test(label, fn) {
    try {
        fn();
        console.log(`  ✓ ${label}`);
        passed++;
    } catch (err) {
        console.error(`  ✗ ${label}`);
        console.error(`    ${err.message}`);
        failed++;
    }
}

console.log('\n── Constraint Engine: Validation ──');

test('HARD rule: load > 400 without 40x40 profile → error', () => {
    const results = validateConfiguration(
        { stateId: 'a0000000-0000-0000-0000-000000000001', dimensions: { width: 1000, height: 2000, depth: 300 }, load: 500, selectedProfile: 'profile_30x30' },
        { includePass: false }
    );
    const errors = results.filter(r => r.status === 'error');
    assert(errors.length > 0, 'Should have errors for wrong profile with heavy load');
    assert(errors.some(e => e.ruleId === 'hr1'), 'Hard rule hr1 should fire');
});

test('HARD rule: load > 400 with 40x40 profile → pass', () => {
    const results = validateConfiguration(
        { stateId: 'a0000000-0000-0000-0000-000000000002', dimensions: { width: 1000, height: 2000, depth: 300 }, load: 500, selectedProfile: 'profile_40x40' },
        { includePass: false }
    );
    const errors = results.filter(r => r.status === 'error');
    assert(errors.length === 0, `Should have no errors but got: ${errors.map(e => e.ruleId).join(', ')}`);
});

test('AUTO rule: toilet module → depth auto_corrected if < 300', () => {
    const results = validateConfiguration(
        { stateId: 'a0000000-0000-0000-0000-000000000003', dimensions: { width: 1000, height: 2000, depth: 200 }, equipmentModules: ['toilet'] },
        { includePass: true }
    );
    const autocorrected = results.filter(r => r.status === 'auto_corrected');
    assert(autocorrected.some(r => r.ruleId === 'ar1'), 'AUTO rule ar1 should trigger auto_corrected');
});

test('SOFT rule: width > 2000 → warning', () => {
    const results = validateConfiguration(
        { stateId: 'a0000000-0000-0000-0000-000000000004', dimensions: { width: 2500, height: 2000, depth: 300 } },
        { includePass: false }
    );
    const warnings = results.filter(r => r.status === 'warning');
    assert(warnings.some(r => r.ruleId === 'sr1'), 'Soft rule sr1 should produce warning for width > 2000');
});

test('Schema validation: missing required fields → schema errors', () => {
    const results = validateConfiguration({}, { includePass: false });
    assert(results.length > 0, 'Empty input should produce validation errors');
});

console.log('\n── Reverse Solver ──');

test('solveReverse: returns solutions array', () => {
    const result = solveReverse({ width: 1000, height: 2000, depth: 300 });
    assert(Array.isArray(result.solutions), 'Should return solutions array');
});

test('solveReverse: valid solutions have no errors', () => {
    const result = solveReverse({ width: 1000, height: 2000, depth: 300 });
    for (const s of result.solutions) {
        assert(!s.validation.some(v => v.status === 'error'), `Solution ${s.rank} should have no errors`);
    }
});

test('solveReverse: solutions ranked by score ascending', () => {
    const result = solveReverse({ width: 1000, height: 2000, depth: 300 });
    for (let i = 1; i < result.solutions.length; i++) {
        assert(result.solutions[i].score >= result.solutions[i - 1].score, 'Solutions should be ranked ascending');
    }
});

test('solveReverse: heavy load generates candidates', () => {
    const result = solveReverse({ width: 1000, height: 2000, depth: 300, load: 500 });
    assert(result.evaluatedCandidates > 0, 'Should evaluate some candidates');
});

console.log('\n── CPQ Engine ──');

test('calculateCpq: returns required PriceQuote fields', () => {
    const snapshot = {
        stateId: 'b0000000-0000-0000-0000-000000000001',
        dimensions: { width: 1000, height: 2000, depth: 300 },
        bom: [{ article: 'profile_40x40', qty: 2000, uom: 'mm' }]
    };
    const quote = calculateCpq(snapshot);
    assert(quote.quoteId, 'Should have quoteId');
    assert(quote.currency === 'RUB', 'Default currency is RUB');
    assert(typeof quote.totalPrice === 'number', 'totalPrice should be a number');
    assert(Array.isArray(quote.lines), 'Quote should have lines');
    assert(quote.lines.length > 0, 'Quote lines should not be empty');
});

test('calculateCpq: VAT 20% calculated correctly', () => {
    const snapshot = {
        stateId: 'b0000000-0000-0000-0000-000000000002',
        dimensions: { width: 1000, height: 2000, depth: 300 },
        bom: [{ article: 'fastener_m6', qty: 10, uom: 'pcs' }]
    };
    const quote = calculateCpq(snapshot);
    const expectedTax = Math.round(quote.subtotal * 0.20 * 100) / 100;
    assert(Math.abs(quote.taxes - expectedTax) < 0.01, `Taxes should be 20% of subtotal, got ${quote.taxes} vs ${expectedTax}`);
});

test('calculateCpq: empty BOM returns zero quote', () => {
    const snapshot = { stateId: 'b0000000-0000-0000-0000-000000000003', dimensions: { width: 1000, height: 2000, depth: 300 }, bom: [] };
    const quote = calculateCpq(snapshot);
    assert(quote.totalPrice === 0, 'Empty BOM should result in zero total');
});

console.log(`\n── Results: ${passed} passed, ${failed} failed ──\n`);
if (failed > 0) process.exit(1);
