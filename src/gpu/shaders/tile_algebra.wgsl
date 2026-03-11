/**
 * Tile Algebra Operations - WGSL Shader Library
 *
 * Implements GPU-accelerated tile algebra operations:
 * 1. Composition Operations (⊗, ⊕) - Tile combination and merging
 * 2. Zone Computations - Spatial region calculations
 * 3. Confidence Propagation - Confidence flow between tiles
 * 4. Parallel Tile Processing - Batch operations on tile arrays
 *
 * Based on POLLN Tile Algebra Formalization:
 * - Tile composition with confidence weights
 * - Zone-based spatial reasoning
 * - Confidence cascade integration
 * - Geometric tensor relationships
 */

// ============================================================================
// STRUCTURES AND TYPES
// ============================================================================

/**
 * Tile - Basic unit of tile algebra
 */
struct Tile {
  id: u32,
  position: vec2<f32>,      // Center position (x, y)
  size: vec2<f32>,          // Width and height
  rotation: f32,            // Rotation angle in radians
  confidence: f32,          // Confidence value [0, 1]
  zone_id: u32,             // Zone membership
  tile_type: u32,           // Type identifier
  properties: array<f32, 8> // Custom properties
};

/**
 * Zone - Spatial region containing tiles
 */
struct Zone {
  id: u32,
  bounds: vec4<f32>,        // (min_x, min_y, max_x, max_y)
  center: vec2<f32>,
  radius: f32,
  zone_type: u32,
  confidence: f32,
  tile_count: u32,
  neighbor_zones: array<u32, 8>
};

/**
 * Composition Rule - Rule for combining tiles
 */
struct CompositionRule {
  rule_id: u32,
  input_types: array<u32, 4>,    // Input tile types
  output_type: u32,              // Output tile type
  confidence_threshold: f32,     // Minimum confidence for composition
  spatial_constraint: u32,       // Spatial relationship required
  weight_matrix: array<f32, 16>  // 4x4 weight matrix for composition
};

/**
 * Composition Result - Result of tile composition
 */
struct CompositionResult {
  success: u32,              // 1 if composition succeeded
  output_tile: Tile,         // Resulting tile
  confidence_gain: f32,      // Change in confidence
  energy_cost: f32,          // Computational cost
  rule_applied: u32          // ID of rule applied
};

// ============================================================================
// CONSTANTS
// ============================================================================

/**
 * Composition operation types
 */
const COMPOSITION_DIRECT_SUM: u32 = 0u;      // ⊕ (direct sum)
const COMPOSITION_TENSOR_PRODUCT: u32 = 1u;  // ⊗ (tensor product)
const COMPOSITION_FUSION: u32 = 2u;          // Fusion (weighted combination)
const COMPOSITION_INTERSECTION: u32 = 3u;    // Intersection
const COMPOSITION_UNION: u32 = 4u;           // Union
const COMPOSITION_DIFFERENCE: u32 = 5u;      // Difference

/**
 * Spatial relationship types
 */
const SPATIAL_ADJACENT: u32 = 0u;
const SPATIAL_OVERLAPPING: u32 = 1u;
const SPATIAL_CONTAINED: u32 = 2u;
const SPATIAL_CONTAINING: u32 = 3u;
const SPATIAL_DISJOINT: u32 = 4u;
const SPATIAL_TOUCHING: u32 = 5u;
const SPATIAL_NEAR: u32 = 6u;
const SPATIAL_FAR: u32 = 7u;

/**
 * Zone types
 */
const ZONE_REGULAR: u32 = 0u;
const ZONE_BOUNDARY: u32 = 1u;
const ZONE_INTERSECTION: u32 = 2u;
const ZONE_CLUSTER: u32 = 3u;
const ZONE_HIERARCHICAL: u32 = 4u;
const ZONE_TEMPORAL: u32 = 5u;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Check if point is inside rectangle
 */
fn point_in_rect(point: vec2<f32>, rect: vec4<f32>) -> bool {
  return point.x >= rect.x && point.x <= rect.z &&
         point.y >= rect.y && point.y <= rect.w;
}

/**
 * Check if two rectangles overlap
 */
fn rects_overlap(rect1: vec4<f32>, rect2: vec4<f32>) -> bool {
  return !(rect1.z < rect2.x || rect1.x > rect2.z ||
           rect1.w < rect2.y || rect1.y > rect2.w);
}

/**
 * Calculate overlap area between two rectangles
 */
fn rect_overlap_area(rect1: vec4<f32>, rect2: vec4<f32>) -> f32 {
  var x_overlap: f32 = max(0.0, min(rect1.z, rect2.z) - max(rect1.x, rect2.x));
  var y_overlap: f32 = max(0.0, min(rect1.w, rect2.w) - max(rect1.y, rect2.y));
  return x_overlap * y_overlap;
}

/**
 * Calculate distance between two points
 */
fn distance_squared(p1: vec2<f32>, p2: vec2<f32>) -> f32 {
  var dx: f32 = p1.x - p2.x;
  var dy: f32 = p1.y - p2.y;
  return dx * dx + dy * dy;
}

/**
 * Calculate tile bounding box
 */
fn tile_bounds(tile: Tile) -> vec4<f32> {
  var half_size: vec2<f32> = tile.size * 0.5;
  return vec4<f32>(
    tile.position.x - half_size.x,
    tile.position.y - half_size.y,
    tile.position.x + half_size.x,
    tile.position.y + half_size.y
  );
}

/**
 * Check spatial relationship between two tiles
 */
fn check_spatial_relationship(tile1: Tile, tile2: Tile, relationship: u32) -> bool {
  var bounds1: vec4<f32> = tile_bounds(tile1);
  var bounds2: vec4<f32> = tile_bounds(tile2);
  var center_dist2: f32 = distance_squared(tile1.position, tile2.position);
  var size_avg: f32 = (tile1.size.x + tile1.size.y + tile2.size.x + tile2.size.y) * 0.25;

  switch (relationship) {
    case SPATIAL_ADJACENT: {
      var overlap: f32 = rect_overlap_area(bounds1, bounds2);
      return overlap == 0.0 && center_dist2 < size_avg * size_avg * 4.0;
    }
    case SPATIAL_OVERLAPPING: {
      return rects_overlap(bounds1, bounds2);
    }
    case SPATIAL_CONTAINED: {
      return point_in_rect(tile1.position, bounds2) && point_in_rect(tile2.position, bounds1);
    }
    case SPATIAL_CONTAINING: {
      return point_in_rect(tile2.position, bounds1) && point_in_rect(tile1.position, bounds2);
    }
    case SPATIAL_DISJOINT: {
      return !rects_overlap(bounds1, bounds2);
    }
    case SPATIAL_TOUCHING: {
      var overlap: f32 = rect_overlap_area(bounds1, bounds2);
      return overlap == 0.0 && center_dist2 < size_avg * size_avg * 1.5;
    }
    case SPATIAL_NEAR: {
      return center_dist2 < size_avg * size_avg * 9.0;
    }
    case SPATIAL_FAR: {
      return center_dist2 > size_avg * size_avg * 16.0;
    }
    default: {
      return false;
    }
  }
}

// ============================================================================
// TILE COMPOSITION OPERATIONS
// ============================================================================

/**
 * Direct sum composition (⊕)
 * Combines tiles by taking union of properties
 */
fn direct_sum_composition(tile1: Tile, tile2: Tile, weight: f32) -> Tile {
  var result: Tile;

  // Average position weighted by confidence
  var total_confidence: f32 = tile1.confidence + tile2.confidence;
  var weight1: f32 = tile1.confidence / total_confidence;
  var weight2: f32 = tile2.confidence / total_confidence;

  result.position = tile1.position * weight1 + tile2.position * weight2;
  result.size = max(tile1.size, tile2.size); // Take maximum size
  result.rotation = mix(tile1.rotation, tile2.rotation, weight2);
  result.confidence = min(1.0, (tile1.confidence + tile2.confidence) * 0.5 * weight);
  result.zone_id = tile1.zone_id; // Keep first tile's zone
  result.tile_type = tile1.tile_type; // Keep first tile's type

  // Combine properties by weighted average
  for (var i: u32 = 0; i < 8u; i = i + 1u) {
    result.properties[i] = tile1.properties[i] * weight1 + tile2.properties[i] * weight2;
  }

  return result;
}

/**
 * Tensor product composition (⊗)
 * Combines tiles by creating higher-dimensional representation
 */
fn tensor_product_composition(tile1: Tile, tile2: Tile, weight_matrix: array<f32, 16>) -> Tile {
  var result: Tile;

  // For tensor product, create a tile that represents the combination
  // Position is midpoint
  result.position = (tile1.position + tile2.position) * 0.5;

  // Size combines both tiles (geometric mean)
  result.size = sqrt(tile1.size * tile2.size);

  // Rotation is average
  result.rotation = (tile1.rotation + tile2.rotation) * 0.5;

  // Confidence is product (tensor product reduces confidence)
  result.confidence = tile1.confidence * tile2.confidence * 0.8;

  // New zone ID (combination of both)
  result.zone_id = tile1.zone_id * 1000u + tile2.zone_id;

  // New tile type (encoded combination)
  result.tile_type = tile1.tile_type * 1000u + tile2.tile_type;

  // Apply weight matrix to properties
  for (var i: u32 = 0; i < 8u; i = i + 1u) {
    var prop_sum: f32 = 0.0;
    for (var j: u32 = 0; j < 8u; j = j + 1u) {
      var weight_idx: u32 = i * 4u + (j % 4u);
      prop_sum = prop_sum + tile1.properties[j] * weight_matrix[weight_idx];
    }
    for (var j: u32 = 0; j < 8u; j = j + 1u) {
      var weight_idx: u32 = (i + 4u) * 4u + (j % 4u);
      prop_sum = prop_sum + tile2.properties[j] * weight_matrix[weight_idx];
    }
    result.properties[i] = prop_sum;
  }

  return result;
}

/**
 * Fusion composition
 * Weighted combination with confidence-based blending
 */
fn fusion_composition(tile1: Tile, tile2: Tile, fusion_weight: f32) -> Tile {
  var result: Tile;

  // Confidence-based blending
  var blend_factor: f32 = tile2.confidence / (tile1.confidence + tile2.confidence);
  blend_factor = blend_factor * fusion_weight;

  // Interpolate all properties
  result.position = mix(tile1.position, tile2.position, blend_factor);
  result.size = mix(tile1.size, tile2.size, blend_factor);
  result.rotation = mix(tile1.rotation, tile2.rotation, blend_factor);

  // Confidence increases through fusion
  result.confidence = min(1.0, (tile1.confidence + tile2.confidence) * 0.6 + 0.2);

  // Zone ID from higher confidence tile
  result.zone_id = select(tile1.zone_id, tile2.zone_id, tile2.confidence > tile1.confidence);

  // Tile type from fusion (average)
  result.tile_type = (tile1.tile_type + tile2.tile_type) / 2u;

  // Blend properties
  for (var i: u32 = 0; i < 8u; i = i + 1u) {
    result.properties[i] = mix(tile1.properties[i], tile2.properties[i], blend_factor);
  }

  return result;
}

/**
 * Apply composition rule to tiles
 */
fn apply_composition_rule(
  tiles: ptr<function, array<Tile>>,
  rule: CompositionRule,
  tile_indices: array<u32, 4>
) -> CompositionResult {
  var result: CompositionResult;
  result.success = 0u;
  result.confidence_gain = 0.0;
  result.energy_cost = 0.0;
  result.rule_applied = rule.rule_id;

  // Check if we have all required tiles
  var valid_tiles: u32 = 0u;
  var input_tiles: array<Tile, 4>;

  for (var i: u32 = 0; i < 4u; i = i + 1u) {
    if (rule.input_types[i] != 0u) {
      if (tile_indices[i] < arrayLength(&tiles)) {
        var tile: Tile = tiles[tile_indices[i]];
        if (tile.tile_type == rule.input_types[i] && tile.confidence >= rule.confidence_threshold) {
          input_tiles[valid_tiles] = tile;
          valid_tiles = valid_tiles + 1u;
        }
      }
    }
  }

  // Check spatial constraints if required
  if (rule.spatial_constraint != 0u && valid_tiles >= 2u) {
    for (var i: u32 = 0; i < valid_tiles - 1u; i = i + 1u) {
      for (var j: u32 = i + 1u; j < valid_tiles; j = j + 1u) {
        if (!check_spatial_relationship(input_tiles[i], input_tiles[j], rule.spatial_constraint)) {
          return result; // Spatial constraint not satisfied
        }
      }
    }
  }

  if (valid_tiles < 2u) {
    return result; // Not enough valid tiles
  }

  // Apply composition based on rule type (simplified)
  var output_tile: Tile;

  if (valid_tiles == 2u) {
    // Two-tile composition
    output_tile = fusion_composition(input_tiles[0], input_tiles[1], 0.5);
  } else if (valid_tiles == 3u) {
    // Three-tile composition: compose first two, then with third
    var temp_tile: Tile = fusion_composition(input_tiles[0], input_tiles[1], 0.5);
    output_tile = fusion_composition(temp_tile, input_tiles[2], 0.5);
  } else if (valid_tiles == 4u) {
    // Four-tile composition: pairwise then combine
    var temp1: Tile = fusion_composition(input_tiles[0], input_tiles[1], 0.5);
    var temp2: Tile = fusion_composition(input_tiles[2], input_tiles[3], 0.5);
    output_tile = fusion_composition(temp1, temp2, 0.5);
  }

  // Set output type
  output_tile.tile_type = rule.output_type;

  // Calculate confidence gain
  var input_confidence_sum: f32 = 0.0;
  for (var i: u32 = 0; i < valid_tiles; i = i + 1u) {
    input_confidence_sum = input_confidence_sum + input_tiles[i].confidence;
  }
  var avg_input_confidence: f32 = input_confidence_sum / f32(valid_tiles);
  result.confidence_gain = output_tile.confidence - avg_input_confidence;

  // Calculate energy cost (simplified)
  result.energy_cost = f32(valid_tiles) * 0.1;

  result.success = 1u;
  result.output_tile = output_tile;

  return result;
}

// ============================================================================
// ZONE COMPUTATIONS
// ============================================================================

/**
 * Find zone for a tile
 */
fn find_tile_zone(tile: Tile, zones: ptr<function, array<Zone>>, num_zones: u32) -> u32 {
  var best_zone_id: u32 = 0u;
  var best_score: f32 = -1.0;

  for (var i: u32 = 0; i < num_zones; i = i + 1u) {
    var zone: Zone = zones[i];

    // Check if tile center is in zone bounds
    if (point_in_rect(tile.position, zone.bounds)) {
      var distance: f32 = distance_squared(tile.position, zone.center);
      var zone_radius2: f32 = zone.radius * zone.radius;

      // Score based on proximity to center and zone confidence
      var score: f32 = zone.confidence * (1.0 - min(1.0, distance / zone_radius2));

      if (score > best_score) {
        best_score = score;
        best_zone_id = zone.id;
      }
    }
  }

  return best_zone_id;
}

/**
 * Update zone statistics based on tiles
 */
fn update_zone_statistics(
  zone: ptr<function, Zone>,
  tiles: ptr<function, array<Tile>>,
  tile_count: u32
) {
  var tile_positions: array<vec2<f32>, 32>;
  var position_count: u32 = 0u;
  var total_confidence: f32 = 0.0;

  // Collect tiles in this zone
  for (var i: u32 = 0; i < tile_count; i = i + 1u) {
    var tile: Tile = tiles[i];
    if (tile.zone_id == zone.id) {
      tile_positions[position_count] = tile.position;
      position_count = position_count + 1u;
      total_confidence = total_confidence + tile.confidence;
    }
  }

  zone.tile_count = position_count;

  if (position_count == 0u) {
    zone.confidence = zone.confidence * 0.9; // Decay confidence
    return;
  }

  // Update zone center (mean of tile positions)
  var center_sum: vec2<f32> = vec2<f32>(0.0, 0.0);
  for (var i: u32 = 0; i < position_count; i = i + 1u) {
    center_sum = center_sum + tile_positions[i];
  }
  zone.center = center_sum / f32(position_count);

  // Update zone radius (max distance from center)
  var max_distance2: f32 = 0.0;
  for (var i: u32 = 0; i < position_count; i = i + 1u) {
    var dist2: f32 = distance_squared(tile_positions[i], zone.center);
    max_distance2 = max(max_distance2, dist2);
  }
  zone.radius = sqrt(max_distance2) * 1.2; // Add 20% padding

  // Update bounds
  zone.bounds = vec4<f32>(
    zone.center.x - zone.radius,
    zone.center.y - zone.radius,
    zone.center.x + zone.radius,
    zone.center.y + zone.radius
  );

  // Update confidence (average of tile confidences)
  zone.confidence = total_confidence / f32(position_count);
}

/**
 * Find neighboring zones
 */
fn find_neighbor_zones(
  zone: Zone,
  zones: ptr<function, array<Zone>>,
  num_zones: u32,
  max_neighbors: u32
) -> array<u32, 8> {
  var neighbors: array<u32, 8>;
  var neighbor_count: u32 = 0u;

  for (var i: u32 = 0; i < num_zones; i = i + 1u) {
    if (i == zone.id) {
      continue;
    }

    var other_zone: Zone = zones[i];

    // Check if zones overlap or are adjacent
    var center_dist: f32 = distance_squared(zone.center, other_zone.center);
    var combined_radius: f32 = zone.radius + other_zone.radius;

    if (center_dist < combined_radius * combined_radius * 2.25) { // 1.5x combined radius
      neighbors[neighbor_count] = other_zone.id;
      neighbor_count = neighbor_count + 1u;

      if (neighbor_count >= max_neighbors) {
        break;
      }
    }
  }

  // Fill remaining slots with 0
  for (var i: u32 = neighbor_count; i < 8u; i = i + 1u) {
    neighbors[i] = 0u;
  }

  return neighbors;
}

// ============================================================================
// CONFIDENCE PROPAGATION BETWEEN TILES
// ============================================================================

/**
 * Propagate confidence between adjacent tiles
 */
fn propagate_tile_confidence(
  source_tile: ptr<function, Tile>,
  target_tile: ptr<function, Tile>,
  propagation_factor: f32
) -> f32 {
  var distance: f32 = distance_squared(source_tile.position, target_tile.position);
  var max_distance: f32 = max(source_tile.size.x, source_tile.size.y) +
                         max(target_tile.size.x, target_tile.size.y);
  max_distance = max_distance * max_distance;

  // Distance-based attenuation
  var attenuation: f32 = 1.0 / (1.0 + distance / max_distance);

  // Confidence transfer
  var confidence_transfer: f32 = source_tile.confidence * propagation_factor * attenuation;

  // Update target confidence
  target_tile.confidence = min(1.0, target_tile.confidence + confidence_transfer * 0.1);

  // Source confidence decays slightly
  source_tile.confidence = source_tile.confidence * (1.0 - confidence_transfer * 0.05);

  return confidence_transfer;
}

/**
 * Propagate confidence within a zone
 */
fn propagate_confidence_in_zone(
  tiles: ptr<function, array<Tile>>,
  zone_id: u32,
  tile_count: u32,
  propagation_factor: f32
) -> f32 {
  var total_transfer: f32 = 0.0;
  var transfers: u32 = 0u;

  for (var i: u32 = 0; i < tile_count; i = i + 1u) {
    var tile1: Tile = tiles[i];
    if (tile1.zone_id != zone_id) {
      continue;
    }

    for (var j: u32 = i + 1u; j < tile_count; j = j + 1u) {
      var tile2: Tile = tiles[j];
      if (tile2.zone_id != zone_id) {
        continue;
      }

      // Check if tiles are adjacent
      if (check_spatial_relationship(tile1, tile2, SPATIAL_ADJACENT) ||
          check_spatial_relationship(tile1, tile2, SPATIAL_OVERLAPPING)) {
        var transfer: f32 = propagate_tile_confidence(&tile1, &tile2, propagation_factor);
        total_transfer = total_transfer + transfer;
        transfers = transfers + 1u;

        // Update tiles
        tiles[i] = tile1;
        tiles[j] = tile2;
      }
    }
  }

  return transfers > 0u ? total_transfer / f32(transfers) : 0.0;
}

// ============================================================================
// COMPUTE SHADERS
// ============================================================================

/**
 * Compute shader for tile composition
 */
@group(0) @binding(0)
var<storage, read_write> input_tiles: array<Tile>;

@group(0) @binding(1)
var<storage, read_write> composition_rules: array<CompositionRule>;

@group(0) @binding(2)
var<storage, read_write> output_tiles: array<Tile>;

@group(0) @binding(3)
var<storage, read_write> composition_results: array<CompositionResult>;

@group(0) @binding(4)
var<uniform> composition_params: vec4<u32>;  // x: num_tiles, y: num_rules, z: max_outputs, w: operation

@compute @workgroup_size(64)
fn tile_composition_kernel(@builtin(global_invocation_id) global_id: vec3<u32>) {
  let idx: u32 = global_id.x;
  let num_tiles: u32 = composition_params.x;
  let num_rules: u32 = composition_params.y;

  if (idx >= num_rules) {
    return;
  }

  var rule: CompositionRule = composition_rules[idx];

  // Try to find tiles that match this rule
  var matching_tiles: array<u32, 4>;
  var match_count: u32 = 0u;

  for (var i: u32 = 0; i < num_tiles && match_count < 4u; i = i + 1u) {
    var tile: Tile = input_tiles[i];

    // Check if tile matches any input type
    for (var j: u32 = 0; j < 4u; j = j + 1u) {
      if (rule.input_types[j] == tile.tile_type && tile.confidence >= rule.confidence_threshold) {
        matching_tiles[match_count] = i;
        match_count = match_count + 1u;
        break;
      }
    }
  }

  if (match_count >= 2u) {
    // Apply composition rule
    var result: CompositionResult = apply_composition_rule(&input_tiles, rule, matching_tiles);

    if (result.success == 1u) {
      // Store result
      var output_idx: u32 = idx % composition_params.z;
      output_tiles[output_idx] = result.output_tile;
      composition_results[idx] = result;
    }
  }
}

/**
 * Compute shader for zone assignment
 */
@group(0) @binding(0)
var<storage, read_write> tiles: array<Tile>;

@group(0) @binding(1)
var<storage, read_write> zones: array<Zone>;

@group(0) @binding(2)
var<storage, read_write> zone_stats: array<vec4<f32>>;  // x: tile_count, y: avg_confidence, z: radius, w: zone_confidence

@group(0) @binding(3)
var<uniform> zone_params: vec4<u32>;  // x: num_tiles, y: num_zones, z: update_mode, w: max_iterations

@compute @workgroup_size(64)
fn zone_assignment_kernel(@builtin(global_invocation_id) global_id: vec3<u32>) {
  let idx: u32 = global_id.x;
  let num_tiles: u32 = zone_params.x;
  let num_zones: u32 = zone_params.y;

  if (idx >= num_tiles) {
    return;
  }

  var tile: Tile = tiles[idx];

  // Find best zone for this tile
  var best_zone_id: u32 = find_tile_zone(tile, &zones, num_zones);

  // Update tile zone
  tile.zone_id = best_zone_id;
  tiles[idx] = tile;

  // Update zone statistics if this is the last thread
  if (idx == num_tiles - 1u) {
    for (var i: u32 = 0; i < num_zones; i = i + 1u) {
      update_zone_statistics(&zones[i], &tiles, num_tiles);

      // Update zone stats buffer
      var zone: Zone = zones[i];
      zone_stats[i] = vec4<f32>(
        f32(zone.tile_count),
        zone.confidence,
        zone.radius,
        zone.confidence
      );
    }
  }
}

/**
 * Compute shader for confidence propagation
 */
@group(0) @binding(0)
var<storage, read_write> tile_array: array<Tile>;

@group(0) @binding(1)
var<storage, read_write> propagation_buffer: array<f32>;

@group(0) @binding(2)
var<uniform> propagation_params: vec4<f32>;  // x: propagation_factor, y: decay_rate, z: min_confidence, w: num_tiles

@compute @workgroup_size(64)
fn confidence_propagation_kernel(@builtin(global_invocation_id) global_id: vec3<u32>) {
  let idx: u32 = global_id.x;
  let num_tiles: u32 = u32(propagation_params.w);

  if (idx >= num_tiles) {
    return;
  }

  var tile: Tile = tile_array[idx];

  // Skip tiles with low confidence
  if (tile.confidence < propagation_params.z) {
    return;
  }

  var total_propagation: f32 = 0.0;
  var propagation_count: u32 = 0u;

  // Propagate to nearby tiles
  for (var i: u32 = 0; i < num_tiles; i = i + 1u) {
    if (i == idx) {
      continue;
    }

    var other_tile: Tile = tile_array[i];

    // Check spatial relationship
    if (check_spatial_relationship(tile, other_tile, SPATIAL_ADJACENT) ||
        check_spatial_relationship(tile, other_tile, SPATIAL_OVERLAPPING)) {
      var propagation: f32 = propagate_tile_confidence(&tile, &other_tile, propagation_params.x);
      total_propagation = total_propagation + propagation;
      propagation_count = propagation_count + 1u;

      // Update other tile
      tile_array[i] = other_tile;
    }
  }

  // Apply decay to current tile
  tile.confidence = tile.confidence * (1.0 - propagation_params.y);

  // Update current tile
  tile_array[idx] = tile;

  // Store propagation result
  propagation_buffer[idx] = propagation_count > 0u ? total_propagation / f32(propagation_count) : 0.0;
}

/**
 * Compute shader for batch tile operations
 */
@group(0) @binding(0)
var<storage, read_write> batch_tiles: array<Tile>;

@group(0) @binding(1)
var<storage, read_write> batch_results: array<vec4<f32>>;

@group(0) @binding(2)
var<uniform> batch_tile_params: vec4<u32>;  // x: batch_size, y: operation, z: tile_type_filter, w: zone_filter

@compute @workgroup_size(64)
fn batch_tile_operations(@builtin(global_invocation_id) global_id: vec3<u32>) {
  let idx: u32 = global_id.x;
  let batch_size: u32 = batch_tile_params.x;
  let operation: u32 = batch_tile_params.y;

  if (idx >= batch_size) {
    return;
  }

  var tile: Tile = batch_tiles[idx];

  // Apply filters
  if (batch_tile_params.z != 0u && tile.tile_type != batch_tile_params.z) {
    return;
  }
  if (batch_tile_params.w != 0u && tile.zone_id != batch_tile_params.w) {
    return;
  }

  var result: vec4<f32> = vec4<f32>(0.0, 0.0, 0.0, 0.0);

  switch (operation) {
    case 0u: { // Calculate statistics
      result.x = tile.confidence;
      result.y = length(tile.position);
      result.z = tile.size.x * tile.size.y; // Area
      result.w = f32(tile.tile_type);
      break;
    }
    case 1u: { // Normalize properties
      var prop_sum: f32 = 0.0;
      for (var i: u32 = 0; i < 8u; i = i + 1u) {
        prop_sum = prop_sum + abs(tile.properties[i]);
      }
      if (prop_sum > 0.0) {
        for (var i: u32 = 0; i < 8u; i = i + 1u) {
          tile.properties[i] = tile.properties[i] / prop_sum;
        }
      }
      result.x = prop_sum;
      break;
    }
    case 2u: { // Apply confidence decay
      tile.confidence = tile.confidence * 0.95;
      result.x = tile.confidence;
      break;
    }
    case 3u: { // Calculate zone affinity
      var zone_affinity: f32 = 1.0 / (1.0 + distance_squared(tile.position, vec2<f32>(0.0, 0.0)));
      result.x = zone_affinity;
      result.y = tile.confidence * zone_affinity;
      break;
    }
  }

  batch_tiles[idx] = tile;
  batch_results[idx] = result;
}

// ============================================================================
// MAIN ENTRY POINTS
// ============================================================================

/**
 * Main tile algebra processing function
 */
fn process_tile_algebra(
  tiles: ptr<function, array<Tile>>,
  zones: ptr<function, array<Zone>>,
  rules: ptr<function, array<CompositionRule>>,
  num_tiles: u32,
  num_zones: u32,
  num_rules: u32,
  time_step: f32
) {
  // 1. Assign tiles to zones
  for (var i: u32 = 0; i < num_tiles; i = i + 1u) {
    var tile: Tile = tiles[i];
    tile.zone_id = find_tile_zone(tile, zones, num_zones);
    tiles[i] = tile;
  }

  // 2. Update zone statistics
  for (var i: u32 = 0; i < num_zones; i = i + 1u) {
    update_zone_statistics(&zones[i], tiles, num_tiles);
  }

  // 3. Propagate confidence within zones
  for (var i: u32 = 0; i < num_zones; i = i + 1u) {
    propagate_confidence_in_zone(tiles, zones[i].id, num_tiles, 0.5);
  }

  // 4. Apply composition rules (simplified - first matching rule)
  for (var i: u32 = 0; i < num_rules && i < num_tiles; i = i + 1u) {
    var rule: CompositionRule = rules[i];
    var tile_indices: array<u32, 4> = array<u32, 4>(i, (i + 1u) % num_tiles, (i + 2u) % num_tiles, (i + 3u) % num_tiles);
    var result: CompositionResult = apply_composition_rule(tiles, rule, tile_indices);

    if (result.success == 1u) {
      // Add new tile to end of array (if space)
      if (num_tiles < arrayLength(&tiles)) {
        tiles[num_tiles] = result.output_tile;
        // Note: num_tiles would need to be updated by caller
      }
    }
  }
}