/**
 * Known-answer control for PlinkoLayer's entropy.
 *
 * The function it pins is reached only through `PlinkoLayer.evaluate`, so these
 * cases drive the real code path rather than a re-implementation: a test that
 * re-derives the answer cannot catch the code being wrong.
 */
import { PlinkoLayer, type AgentProposal } from '../decision.js';

function proposals(confidences: number[]): AgentProposal[] {
  return confidences.map((confidence, i) => ({
    agentId: `a${i}`,
    confidence,
  })) as AgentProposal[];
}

function entropyOf(confidences: number[]): number {
  const layer = new PlinkoLayer({ temperature: 0.5, minTemperature: 0.1 });
  return layer.evaluate(proposals(confidences)).entropy;
}

describe('entropy — known-answer control', () => {
  it('is zero for a single proposal (a distribution on one point carries no surprise)', () => {
    expect(entropyOf([0.9])).toBeCloseTo(0, 10);
  });

  it('is ln(n) for a uniform distribution — the maximum', () => {
    expect(entropyOf([0.5, 0.5, 0.5])).toBeCloseTo(Math.log(3), 10);
    expect(entropyOf([0.25, 0.25, 0.25, 0.25])).toBeCloseTo(Math.log(4), 10);
  });

  it('is never negative — the old formula returned -2.099 for a healthy pool', () => {
    for (const c of [[0.5, 0.5, 0.5], [0.98, 0.01, 0.01], [0.4, 0.35, 0.25], [0.3, 0.3, 0.2, 0.2]]) {
      expect(entropyOf(c)).toBeGreaterThanOrEqual(0);
    }
  });

  it('points the RIGHT WAY: a healthy pool outscores a collapsed one', () => {
    // This is the assertion the old formula inverted. A detector reading
    // "low entropy => mode collapse" was firing on healthy pools.
    const healthy = entropyOf([0.5, 0.5, 0.5]);
    const collapsed = entropyOf([0.98, 0.01, 0.01]);
    expect(healthy).toBeGreaterThan(collapsed);
  });

  it('is zero for all-zero confidences and must NOT be NaN', () => {
    // Old code: 0/0 -> NaN, and NaN flowed silently into PlinkoResult.entropy.
    const e = entropyOf([0, 0, 0]);
    expect(Number.isNaN(e)).toBe(false);
    expect(e).toBe(0);
  });

  it('is finite for an empty proposal list', () => {
    const layer = new PlinkoLayer({ temperature: 0.5, minTemperature: 0.1 });
    const r = layer.evaluate([]);
    expect(Number.isFinite(r.entropy)).toBe(true);
  });

  it('is invariant to scale — entropy is a function of the SHAPE, not the magnitude', () => {
    expect(entropyOf([0.5, 0.5, 0.5])).toBeCloseTo(entropyOf([0.25, 0.25, 0.25]), 10);
  });
});
