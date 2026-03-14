#!/bin/bash

# SuperInstance Research Platform - API Examples
# ===============================================

BASE_URL="http://localhost:8000"

echo "SuperInstance Research Platform - API Examples"
echo "=============================================="
echo ""

# Example 1: Health Check
echo "1. Health Check"
echo "GET /health"
curl -s "${BASE_URL}/health" | jq '.'
echo -e "\n"

# Example 2: Platform Stats
echo "2. Platform Statistics"
echo "GET /stats"
curl -s "${BASE_URL}/stats" | jq '.'
echo -e "\n"

# Example 3: Run Simple Simulation
echo "3. Run Simulation"
echo "POST /simulate"
curl -s -X POST "${BASE_URL}/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_id": "api_example_001",
    "name": "API Example Simulation",
    "simulation_type": "gpu_accelerated",
    "parameters": {
      "matrix_size": 500,
      "iterations": 50
    },
    "backend_preference": "auto",
    "validation_types": ["sanity"]
  }' | jq '.'
echo -e "\n"

# Example 4: Run Async Simulation
echo "4. Run Async Simulation"
echo "POST /simulate/async"
curl -s -X POST "${BASE_URL}/simulate/async" \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_id": "api_example_002",
    "name": "Async API Example",
    "simulation_type": "gpu_accelerated",
    "parameters": {
      "matrix_size": 1000,
      "iterations": 100
    }
  }' | jq '.'
echo -e "\n"

# Example 5: Check Status
echo "5. Check Experiment Status"
echo "GET /status/api_example_002"
curl -s "${BASE_URL}/status/api_example_002" | jq '.'
echo -e "\n"

# Example 6: Get Results
echo "6. Get Experiment Results"
echo "GET /results/api_example_001"
curl -s "${BASE_URL}/results/api_example_001" | jq '.'
echo -e "\n"

# Example 7: List Experiments
echo "7. List All Experiments"
echo "GET /experiments"
curl -s "${BASE_URL}/experiments" | jq '.'
echo -e "\n"

# Example 8: List Filtered Experiments
echo "8. List Experiments by Tag"
echo "GET /experiments?tag=demo"
curl -s "${BASE_URL}/experiments?tag=demo" | jq '.'
echo -e "\n"

# Example 9: Validate Results
echo "9. Validate Experiment Results"
echo "POST /validate"
curl -s -X POST "${BASE_URL}/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_id": "api_example_001",
    "validation_types": ["statistical", "sanity"]
  }' | jq '.'
echo -e "\n"

# Example 10: Compare Experiments
echo "10. Compare Multiple Experiments"
echo "POST /compare"
curl -s -X POST "${BASE_URL}/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_ids": ["api_example_001", "api_example_002"],
    "comparison_type": "performance"
  }' | jq '.'
echo -e "\n"

# Example 11: Prepare Publication
echo "11. Prepare Publication Package"
echo "POST /publication?paper_id=P24&experiment_ids=api_example_001&experiment_ids=api_example_002"
curl -s -X POST "${BASE_URL}/publication?paper_id=P24&experiment_ids=api_example_001&experiment_ids=api_example_002" | jq '.'
echo -e "\n"

# Example 12: Delete Experiment
echo "12. Delete Experiment"
echo "DELETE /experiments/api_example_001"
curl -s -X DELETE "${BASE_URL}/experiments/api_example_001" | jq '.'
echo -e "\n"

echo "Examples completed!"
