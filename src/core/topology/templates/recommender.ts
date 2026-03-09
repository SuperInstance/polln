/**
 * Topology recommendation engine
 * Recommends optimal topology based on requirements
 */

import { TOPOLOGY_TEMPLATES } from './templates';
import { TopologyTemplate } from './types';

export interface Requirements {
  colonySize: number;
  prioritizeEfficiency?: boolean;
  prioritizeRobustness?: boolean;
  prioritizeLowCost?: boolean;
  workloadPattern?: 'uniform' | 'hotspot' | 'hierarchical' | 'local';
}

/**
 * Recommend optimal topology based on requirements
 */
export function recommendTopology(requirements: Requirements): TopologyTemplate | null {
  const { colonySize, prioritizeEfficiency, prioritizeRobustness, prioritizeLowCost, workloadPattern } = requirements;

  // Filter by size
  let candidates = Object.values(TOPOLOGY_TEMPLATES).filter(
    t => colonySize >= t.colonySizeRange[0] && colonySize <= t.colonySizeRange[1]
  );

  if (candidates.length === 0) return null;

  // Sort by priority
  candidates = candidates.sort((a, b) => {
    let scoreA = 0, scoreB = 0;

    if (prioritizeEfficiency) {
      scoreA += a.expectedMetrics.globalEfficiency * 2;
      scoreB += b.expectedMetrics.globalEfficiency * 2;
    }

    if (prioritizeRobustness) {
      scoreA += (a.expectedMetrics.attackTolerance + a.expectedMetrics.failureTolerance);
      scoreB += (b.expectedMetrics.attackTolerance + b.expectedMetrics.failureTolerance);
    }

    if (prioritizeLowCost) {
      scoreA += (1 - a.expectedMetrics.edgeCost) * 2;
      scoreB += (1 - b.expectedMetrics.edgeCost) * 2;
    }

    return scoreB - scoreA;
  });

  return candidates[0];
}

/**
 * Compare multiple topology templates
 */
export function compareTemplates(templateNames: string[]): Record<string, any> {
  const comparison: Record<string, any> = {};

  for (const name of templateNames) {
    const template = TOPOLOGY_TEMPLATES[name];
    if (template) {
      comparison[name] = {
        avgPathLength: template.expectedMetrics.avgPathLength,
        clustering: template.expectedMetrics.clusteringCoeff,
        efficiency: template.expectedMetrics.globalEfficiency,
        robustness: (template.expectedMetrics.attackTolerance + template.expectedMetrics.failureTolerance) / 2,
        cost: template.expectedMetrics.edgeCost,
      };
    }
  }

  return comparison;
}
