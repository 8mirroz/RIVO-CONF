'use strict';

const { randomUUID } = require('crypto');

/**
 * CPQ Engine — server-side pricing and BOM calculation.
 * P2-02: Pricing and BOM strictly from StructureGraph + config.
 * For Phase 1/2, uses rule-based pricing from BOM items.
 */

// Default price list per article (RUB/unit). Will be replaced by catalog pricing in Phase 2.
const DEFAULT_PRICE_LIST = {
    profile_30x30: 450,    // RUB per meter (mm/1000 * price)
    profile_40x40: 680,
    fastener_m6: 12,
    node_t: 85,
    node_corner: 95,
    DEFAULT: 100
};

function unitPrice(article) {
    return DEFAULT_PRICE_LIST[article] || DEFAULT_PRICE_LIST.DEFAULT;
}

function bomToLines(bom) {
    if (!Array.isArray(bom)) return [];
    return bom
        .filter(item => (item.article || item.sku) && item.qty)
        .map(item => {
            const art = item.article || item.sku;
            const qty = Number(item.qty) || 0;
            const uom = item.uom || item.unit || 'pcs';
            const up = unitPrice(art);
            // For mm uom, convert to meters for pricing
            const effectiveQty = uom === 'mm' ? qty / 1000 : qty;
            const lineTotal = Math.round(up * effectiveQty * 100) / 100;
            return {
                article: art,
                name: item.name || art,
                qty,
                uom,
                unitPrice: up,
                total: lineTotal
            };
        });
}

function calculateCpq(snapshot) {
    const bom = snapshot && Array.isArray(snapshot.bom) ? snapshot.bom : [];
    const lines = bomToLines(bom);
    const subtotal = Math.round(lines.reduce((sum, l) => sum + l.total, 0) * 100) / 100;
    const discounts = 0;
    const taxes = Math.round(subtotal * 0.20 * 100) / 100; // VAT 20%
    const totalPrice = Math.round((subtotal + taxes - discounts) * 100) / 100;

    return {
        quoteId: randomUUID(),
        currency: 'RUB',
        subtotal,
        discounts,
        taxes,
        totalPrice,
        total: totalPrice,
        lines
    };
}

module.exports = { calculateCpq, bomToLines };
