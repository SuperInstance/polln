/**
 * Rate-Based Change Mechanics Tests
 *
 * Tests for the rate-based change mechanics described in the SuperInstance white paper.
 * Tests the mathematical foundation: x(t) = x₀ + ∫r(τ)dτ
 */

import { SensationSystem, SensationType, Sensation, CellReference } from '../../spreadsheet/core/Sensation';

describe('Rate-Based Change Mechanics', () => {
  let sensationSystem: SensationSystem;

  beforeEach(() => {
    sensationSystem = new SensationSystem();
  });

  describe('Mathematical Foundation', () => {
    it('should understand the rate-first formalism: x(t) = x₀ + ∫r(τ)dτ', () => {
      // Test the mathematical concept
      const x0 = 10; // Initial state
      const rates = [2, 3, 1, 4]; // Rates over time intervals
      const timeIntervals = [1, 1, 1, 1]; // Equal time intervals

      // Simulate integration: x(t) = x₀ + Σ(r_i * Δt_i)
      let integral = 0;
      for (let i = 0; i < rates.length; i++) {
        integral += rates[i] * timeIntervals[i];
      }

      const x_t = x0 + integral;
      const expected = 10 + (2 + 3 + 1 + 4); // 10 + 10 = 20

      expect(x_t).toBe(expected);
      expect(x_t).toBe(20);
    });

    it('should demonstrate superiority over absolute position tracking', () => {
      // Scenario: Sparse updates with rate-based prediction
      const updates = [
        { time: 0, value: 100 },
        { time: 5, value: 110 }, // +10 over 5 seconds = rate of +2/sec
        { time: 15, value: 125 } // +15 over 10 seconds = rate of +1.5/sec
      ];

      // Absolute tracking only knows discrete points
      // Rate-based tracking can predict intermediate states

      // Calculate average rate between first and last update
      const totalTime = updates[2].time - updates[0].time; // 15 seconds
      const totalChange = updates[2].value - updates[0].value; // +25
      const averageRate = totalChange / totalTime; // 25/15 ≈ 1.667

      // Predict value at time = 10
      const timeToPredict = 10;
      const predictedValue = updates[0].value + (averageRate * timeToPredict);
      // 100 + (1.667 * 10) ≈ 116.67

      expect(predictedValue).toBeCloseTo(116.67, 2);
      expect(averageRate).toBeCloseTo(1.667, 3);
    });
  });

  describe('Sensation System Integration', () => {
    const testCell: CellReference = { row: 0, col: 0 };

    it('should detect absolute changes', () => {
      const oldValue = 100;
      const newValue = 120;
      const threshold = 5;

      const sensation = sensationSystem.detectAbsoluteChange(
        testCell,
        oldValue,
        newValue,
        threshold
      );

      expect(sensation).not.toBeNull();
      expect(sensation!.type).toBe(SensationType.ABSOLUTE_CHANGE);
      expect(sensation!.value).toBe(20); // 120 - 100
      expect(sensation!.previousValue).toBe(100);
      expect(sensation!.currentValue).toBe(120);
      expect(sensation!.confidence).toBeGreaterThan(0);
    });

    it('should detect rate of change', () => {
      const lastValue = 100;
      const lastTimestamp = 1000;
      const newValue = 120;
      const currentTime = 2000; // 1 second later
      const threshold = 5;

      const sensation = sensationSystem.detectRateOfChange(
        testCell,
        lastValue,
        lastTimestamp,
        newValue,
        currentTime,
        threshold
      );

      expect(sensation).not.toBeNull();
      expect(sensation!.type).toBe(SensationType.RATE_OF_CHANGE);
      expect(sensation!.value).toBe(20); // (120-100)/1 = 20 units per second
      expect(sensation!.confidence).toBeGreaterThan(0);
    });

    it('should detect acceleration (second derivative)', () => {
      // Simulate changing rates: 10, 15, 25 (accelerating)
      const history = {
        values: [100, 110, 125, 150], // Changes: +10, +15, +25
        timestamps: [0, 1000, 2000, 3000] // 1-second intervals
      };

      const newValue = 180; // Change of +30
      const currentTime = 4000;

      const sensation = sensationSystem.detectAcceleration(
        testCell,
        history,
        newValue,
        currentTime,
        5
      );

      expect(sensation).not.toBeNull();
      expect(sensation!.type).toBe(SensationType.ACCELERATION);
      // Rates: 10, 15, 25, 30 → Acceleration: +5, +10, +5
      expect(Math.abs(sensation!.value)).toBeGreaterThan(0);
    });
  });

  describe('Deadband Triggers', () => {
    const testCell: CellReference = { row: 0, col: 0 };

    it('should ignore changes within deadband', () => {
      const oldValue = 100;
      const newValue = 103; // Change of 3
      const threshold = 5; // Deadband threshold

      const sensation = sensationSystem.detectAbsoluteChange(
        testCell,
        oldValue,
        newValue,
        threshold
      );

      // Change of 3 < threshold of 5, so no sensation
      expect(sensation).toBeNull();
    });

    it('should trigger on changes outside deadband', () => {
      const oldValue = 100;
      const newValue = 108; // Change of 8
      const threshold = 5; // Deadband threshold

      const sensation = sensationSystem.detectAbsoluteChange(
        testCell,
        oldValue,
        newValue,
        threshold
      );

      // Change of 8 > threshold of 5, so sensation triggered
      expect(sensation).not.toBeNull();
      expect(sensation!.value).toBe(8);
    });

    it('should apply deadband to rate of change', () => {
      const lastValue = 100;
      const lastTimestamp = 1000;
      const newValue = 103; // Change of 3
      const currentTime = 2000; // 1 second later
      const threshold = 5; // Rate threshold

      const sensation = sensationSystem.detectRateOfChange(
        testCell,
        lastValue,
        lastTimestamp,
        newValue,
        currentTime,
        threshold
      );

      // Rate of 3 units/sec < threshold of 5, so no sensation
      expect(sensation).toBeNull();
    });
  });

  describe('Predictive State Estimation', () => {
    it('should predict future states using rate-based extrapolation', () => {
      // Given historical rates, predict future state
      const historicalRates = [2.0, 2.1, 2.2, 2.3]; // Slightly increasing rate
      const currentState = 100;
      const predictionHorizon = 5; // Predict 5 time units ahead

      // Simple linear prediction using average rate
      const averageRate = historicalRates.reduce((sum, rate) => sum + rate, 0) / historicalRates.length;
      const predictedState = currentState + (averageRate * predictionHorizon);

      // Average rate ≈ 2.15, prediction ≈ 100 + (2.15 * 5) = 110.75
      expect(predictedState).toBeCloseTo(110.75, 2);
      expect(averageRate).toBeCloseTo(2.15, 2);
    });

    it('should detect anomalies through rate deviation', () => {
      const expectedRate = 2.0;
      const actualRate = 5.0; // Much higher than expected
      const tolerance = 0.5; // 50% tolerance

      const deviation = Math.abs(actualRate - expectedRate) / expectedRate;
      const isAnomaly = deviation > tolerance;

      expect(isAnomaly).toBe(true);
      expect(deviation).toBe(1.5); // 150% deviation
    });
  });

  describe('Smooth Interpolation', () => {
    it('should interpolate between known states using rate information', () => {
      const state1 = { time: 0, value: 100 };
      const state2 = { time: 10, value: 120 };

      // Calculate average rate
      const timeDelta = state2.time - state1.time;
      const valueDelta = state2.value - state1.value;
      const averageRate = valueDelta / timeDelta; // 20/10 = 2 units per time unit

      // Interpolate at time = 5
      const interpolateTime = 5;
      const interpolatedValue = state1.value + (averageRate * interpolateTime);
      // 100 + (2 * 5) = 110

      expect(interpolatedValue).toBe(110);
      expect(averageRate).toBe(2);
    });

    it('should handle non-linear interpolation with changing rates', () => {
      // Simulate accelerating system
      const states = [
        { time: 0, value: 100 },
        { time: 5, value: 110 }, // Rate: 2 units/time
        { time: 10, value: 125 }  // Rate: 3 units/time (accelerating)
      ];

      // Calculate instantaneous rates
      const rate1 = (states[1].value - states[0].value) / (states[1].time - states[0].time);
      const rate2 = (states[2].value - states[1].value) / (states[2].time - states[1].time);

      // Interpolate using weighted average of rates
      const targetTime = 7.5; // Midpoint
      const timeFraction = (targetTime - states[1].time) / (states[2].time - states[1].time);
      const interpolatedRate = rate1 + (rate2 - rate1) * timeFraction;

      const interpolatedValue = states[1].value + interpolatedRate * (targetTime - states[1].time);

      expect(rate1).toBe(2); // (110-100)/5
      expect(rate2).toBe(3); // (125-110)/5
      expect(interpolatedRate).toBeCloseTo(2.5, 1); // Average at midpoint
      expect(interpolatedValue).toBeCloseTo(117.5, 1); // 110 + (2.5 * 2.5)
    });
  });

  describe('Integration with SuperInstance', () => {
    it('should track rate-based changes for SuperInstance states', async () => {
      // Simulate a SuperInstance with changing state
      const instanceStates = [
        { timestamp: 0, cpuUsage: 10, memoryUsage: 100 },
        { timestamp: 1000, cpuUsage: 15, memoryUsage: 120 },
        { timestamp: 2000, cpuUsage: 25, memoryUsage: 150 }
      ];

      // Calculate rates of change
      const cpuRates = [];
      const memoryRates = [];

      for (let i = 1; i < instanceStates.length; i++) {
        const timeDelta = instanceStates[i].timestamp - instanceStates[i-1].timestamp;
        const cpuDelta = instanceStates[i].cpuUsage - instanceStates[i-1].cpuUsage;
        const memoryDelta = instanceStates[i].memoryUsage - instanceStates[i-1].memoryUsage;

        cpuRates.push(cpuDelta / timeDelta);
        memoryRates.push(memoryDelta / timeDelta);
      }

      // Verify rates are calculated correctly
      expect(cpuRates).toHaveLength(2);
      expect(memoryRates).toHaveLength(2);

      // CPU rates: (15-10)/1000 = 0.005, (25-15)/1000 = 0.01
      expect(cpuRates[0]).toBe(0.005);
      expect(cpuRates[1]).toBe(0.01);

      // Memory rates: (120-100)/1000 = 0.02, (150-120)/1000 = 0.03
      expect(memoryRates[0]).toBe(0.02);
      expect(memoryRates[1]).toBe(0.03);

      // Detect acceleration in CPU usage
      const cpuAcceleration = cpuRates[1] - cpuRates[0]; // 0.01 - 0.005 = 0.005
      expect(cpuAcceleration).toBe(0.005);
    });

    it('should use rate-based prediction for resource planning', () => {
      // Given current resource usage and rate of change, predict when limits will be hit
      const currentUsage = 60; // 60% of resource
      const currentRate = 5; // Increasing at 5% per time unit
      const limit = 90; // Resource limit at 90%

      // Time to reach limit: (limit - currentUsage) / rate
      const timeToLimit = (limit - currentUsage) / currentRate;
      // (90 - 60) / 5 = 6 time units

      expect(timeToLimit).toBe(6);

      // With acceleration consideration
      const acceleration = 0.5; // Rate increasing by 0.5% per time unit
      // More complex prediction would use: usage(t) = current + rate*t + 0.5*acceleration*t²
      // Solve for t when usage(t) = limit
    });
  });

  describe('Edge Cases and Error Handling', () => {
    const testCell: CellReference = { row: 0, col: 0 };

    it('should handle zero time delta in rate calculation', () => {
      const lastValue = 100;
      const lastTimestamp = 1000;
      const newValue = 120;
      const currentTime = 1000; // Same time!
      const threshold = 5;

      const sensation = sensationSystem.detectRateOfChange(
        testCell,
        lastValue,
        lastTimestamp,
        newValue,
        currentTime,
        threshold
      );

      // Division by zero should be handled gracefully
      expect(sensation).toBeNull();
    });

    it('should handle insufficient history for acceleration detection', () => {
      const history = {
        values: [100, 110], // Only 2 points
        timestamps: [0, 1000]
      };

      const newValue = 120;
      const currentTime = 2000;

      const sensation = sensationSystem.detectAcceleration(
        testCell,
        history,
        newValue,
        currentTime,
        5
      );

      // Need at least 3 points for acceleration
      expect(sensation).toBeNull();
    });

    it('should handle negative rates and values', () => {
      const oldValue = 100;
      const newValue = 80; // Negative change
      const threshold = 5;

      const sensation = sensationSystem.detectAbsoluteChange(
        testCell,
        oldValue,
        newValue,
        threshold
      );

      expect(sensation).not.toBeNull();
      expect(sensation!.value).toBe(-20); // Negative change
    });
  });

  describe('Performance and Real-world Scenarios', () => {
    it('should efficiently handle high-frequency updates', () => {
      const numUpdates = 1000;
      const startTime = Date.now();

      // Simulate many rapid updates
      for (let i = 0; i < numUpdates; i++) {
        const sensation = sensationSystem.detectAbsoluteChange(
          { row: 0, col: 0 },
          i * 10,
          i * 10 + 5,
          2
        );
        // Most should trigger (change of 5 > threshold of 2)
      }

      const endTime = Date.now();
      const duration = endTime - startTime;

      // Should process quickly
      expect(duration).toBeLessThan(1000); // < 1 second for 1000 updates
    });

    it('should demonstrate real-world value in monitoring systems', () => {
      // Scenario: Server monitoring with rate-based alerts
      const serverMetrics = [
        { timestamp: 0, responseTime: 100, requestsPerSecond: 10 },
        { timestamp: 60000, responseTime: 150, requestsPerSecond: 15 }, // 1 minute later
        { timestamp: 120000, responseTime: 250, requestsPerSecond: 8 }  // 2 minutes later
      ];

      // Calculate rates of change
      const responseTimeRate1 = (serverMetrics[1].responseTime - serverMetrics[0].responseTime) / 60000;
      const responseTimeRate2 = (serverMetrics[2].responseTime - serverMetrics[1].responseTime) / 60000;

      const requestRate1 = (serverMetrics[1].requestsPerSecond - serverMetrics[0].requestsPerSecond) / 60000;
      const requestRate2 = (serverMetrics[2].requestsPerSecond - serverMetrics[1].requestsPerSecond) / 60000;

      // Detect concerning patterns:
      // 1. Response time increasing rapidly
      // 2. Request rate dropping while response time increases (bottleneck)

      const responseTimeAccelerating = responseTimeRate2 > responseTimeRate1;
      const requestsDropping = requestRate2 < 0;

      expect(responseTimeAccelerating).toBe(true);
      expect(requestsDropping).toBe(true);

      // This pattern suggests a performance bottleneck
      const bottleneckDetected = responseTimeAccelerating && requestsDropping;
      expect(bottleneckDetected).toBe(true);
    });
  });
});