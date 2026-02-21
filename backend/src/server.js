'use strict';

const express = require('express');
const { validateConfiguration, normalizeSnapshotLikeInput } = require('./validation/validationEngine');
const { solveReverse } = require('./solver/reverseSolver');
const { calculateCpq } = require('./cpq/cpqEngine');

const app = express();
app.use(express.json());

// Health check
app.get('/health', (_req, res) => res.json({ status: 'ok', version: '1.1.0' }));

// POST /api/v1/solutions/generate
// Supports both canonical GenerateSolutionsRequest and legacy ConfigurationSnapshot
app.post('/api/v1/solutions/generate', (req, res) => {
    try {
        const body = req.body || {};
        const params = body.requirements || body;
        const result = solveReverse(params, { maxSolutions: 3, dimensionBreadth: 2 });

        const solutions = result.solutions.map((s, i) => {
            const profileTypes = ['economic', 'balanced', 'reinforced'];
            return {
                configurationId: s.snapshot.stateId,
                type: profileTypes[i] || 'balanced',
                structureGraph: s.snapshot.graph || {},
                price: calculateCpq(s.snapshot),
                bom: Array.isArray(s.snapshot.bom) ? s.snapshot.bom : [],
                validationState: s.validation
            };
        });

        res.json({ solutions, exactMatch: result.exactMatch, relaxationHints: result.relaxationHints });
    } catch (err) {
        res.status(400).json({ code: 'GENERATE_ERROR', message: err.message });
    }
});

// POST /api/v1/configurations/validate  (canonical)
// POST /api/v1/configuration/validate   (also handled below)
function handleValidate(req, res) {
    try {
        const results = validateConfiguration(req.body || {}, { includePass: false });
        const valid = results.every(r => r.status !== 'error');
        res.json({ valid, items: results });
    } catch (err) {
        res.status(400).json({ code: 'VALIDATE_ERROR', message: err.message });
    }
}
app.post('/api/v1/configurations/validate', handleValidate);
app.post('/api/v1/configuration/validate', handleValidate);

// POST /api/v1/cpq/calculate
app.post('/api/v1/cpq/calculate', (req, res) => {
    try {
        const snapshot = normalizeSnapshotLikeInput(req.body || {});
        const quote = calculateCpq(snapshot);
        res.json(quote);
    } catch (err) {
        res.status(400).json({ code: 'CPQ_ERROR', message: err.message });
    }
});

// Export stubs (PDF, DXF, IFC) — P4 implementation
app.post('/api/v1/exports/pdf', (_req, res) =>
    res.status(501).json({ code: 'NOT_IMPLEMENTED', message: 'PDF export is planned for Phase 4.' })
);
app.post('/api/v1/exports/dxf', (_req, res) =>
    res.status(501).json({ code: 'NOT_IMPLEMENTED', message: 'DXF export is planned for Phase 4.' })
);
app.post('/api/v1/exports/ifc', (_req, res) =>
    res.status(501).json({ code: 'NOT_IMPLEMENTED', message: 'IFC export is planned for Phase 6.' })
);

const PORT = process.env.PORT || 3001;
const server = app.listen(PORT, () => {
    console.log(`RIVO Backend API v1.1.0 listening on :${PORT}`);
});

module.exports = app;
