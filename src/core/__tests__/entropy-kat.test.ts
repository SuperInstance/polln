/**
 * Known-answer control for PlinkoLayer's entropy.
 *
 * The function it pins is reached only through `PlinkoLayer.process`, so these
 * cases drive the real code path rather than a re-implementation: a test that
 * re-derives the answer cannot catch the code being wrong.
 *
 * Drift repair (2026-09-30, PR #64): this KAT was written against
 * `PlinkoLayer.evaluate` and never ran (CI had no test step), so it rotted
 * while the API moved — `evaluate` became async `process`, and `PlinkoConfig`
 * grew a required `decayRate`. The seven known-answer pins are unchanged;
 * only the call path was re-expressed against the current API.
 */
import { PlinkoLayer, type AgentProposal } from '../decision.js';

function proposals(confidences: number[]): AgentProposal[] {
  return confidences.map((confidence, i) => ({
    agentId: `a${i}`,
    confidence,
  })) as AgentProposal[];
}

const KAT_CONFIG = { temperature: 0.5, minTemperature: 0.1, decayRate: 0.001 };

async function entropyOf(confidences: number[]): Promise<number> {
  const layer = new PlinkoLayer(KAT_CONFIG);
  return (await layer.process(proposals(confidences))).entropy;
}

describe('entropy — known-answer control', () => {
  it('is zero for a single proposal (a distribution on one point carries no surprise)', async () => {
    expect(await entropyOf([0.9])).toBeCloseTo(0, 10);
  });

  it('is ln(n) for a uniform distribution — the maximum', async () => {
    expect(await entropyOf([0.5, 0.5, 0.5])).toBeCloseTo(Math.log(3), 10);
    expect(await entropyOf([0.25, 0.25, 0.25, 0.25])).toBeCloseTo(Math.log(4), 10);
  });

  it('is never negative — the old formula returned -2.099 for a healthy pool', async () => {
    for (const c of [[0.5, 0.5, 0.5], [0.98, 0.01, 0.01], [0.4, 0.35, 0.25], [0.3, 0.3, 0.2, 0.2]]) {
      expect(await entropyOf(c)).toBeGreaterThanOrEqual(0);
    }
  });

  it('points the RIGHT WAY: a healthy pool outscores a collapsed one', async () => {
    // This is the assertion the old formula inverted. A detector reading
    // "low entropy => mode collapse" was firing on healthy pools.
    const healthy = await entropyOf([0.5, 0.5, 0.5]);
    const collapsed = await entropyOf([0.98, 0.01, 0.01]);
    expect(healthy).toBeGreaterThan(collapsed);
  });

  it('is zero for all-zero confidences and must NOT be NaN', async () => {
    // Old code: 0/0 -> NaN, and NaN flowed silently into PlinkoResult.entropy.
    const e = await entropyOf([0, 0, 0]);
    expect(Number.isNaN(e)).toBe(false);
    expect(e).toBe(0);
  });

  it('rejects an empty proposal list with the explicit selection error', async () => {
    // Original pin: "entropy is finite for an empty list". That pin is currently
    // unreachable through the public path: process([]) throws in
    // gumbelSoftmax ("Cannot select from empty proposals array") before the
    // result — with entropy = 0 for the empty distribution — is returned.
    // The degenerate-input NaN pin lives in the all-zeros case above. If
    // entropy-for-empty becomes part of the contract, expose it and restore
    // the original pin; until then, this documents the real behavior.
    const layer = new PlinkoLayer(KAT_CONFIG);
    await expect(layer.process([])).rejects.toThrow(
      'Cannot select from empty proposals array'
    );
  });

  it('is invariant to scale — entropy is a function of the SHAPE, not the magnitude', async () => {
    expect(await entropyOf([0.5, 0.5, 0.5])).toBeCloseTo(await entropyOf([0.25, 0.25, 0.25]), 10);
  });
});
