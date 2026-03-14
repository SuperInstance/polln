#!/bin/bash
###############################################################################
# Distributed Training Deployment Script
#
# Automates deployment of multi-GPU distributed training across nodes.
#
# Usage:
#   ./deploy.sh --nodes 2 --gpu-per-node 4 --master-addr 192.168.1.1
#
# Features:
# - Environment setup
# - Dependency checking
# - Multi-node configuration
# - Training launch
# - Monitoring
###############################################################################

set -e  # Exit on error

###############################################################################
# Configuration
###############################################################################

# Default values
NUM_NODES=1
GPU_PER_NODE=4
MASTER_ADDR="localhost"
MASTER_PORT=29500
BATCH_SIZE=128
EPOCHS=100
LEARNING_RATE=0.001
USE_CRDT=true
USE_AMP=true
COMPRESSION_RATIO=0.1

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/example_cifar10.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

###############################################################################
# Functions
###############################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_banner() {
    echo ""
    echo "================================================================================"
    echo "                    Multi-GPU Distributed Training Deployment"
    echo "================================================================================"
    echo ""
}

print_config() {
    log_info "Deployment Configuration:"
    echo ""
    echo "  Nodes:             ${NUM_NODES}"
    echo "  GPUs per Node:     ${GPU_PER_NODE}"
    echo "  Total GPUs:        $((NUM_NODES * GPU_PER_NODE))"
    echo "  Master Address:    ${MASTER_ADDR}"
    echo "  Master Port:       ${MASTER_PORT}"
    echo "  Batch Size:        ${BATCH_SIZE}"
    echo "  Effective Batch:   $((BATCH_SIZE * NUM_NODES * GPU_PER_NODE))"
    echo "  Epochs:            ${EPOCHS}"
    echo "  Learning Rate:     ${LEARNING_RATE}"
    echo "  CRDT Sync:         ${USE_CRDT}"
    echo "  AMP:               ${USE_AMP}"
    echo "  Compression:       ${COMPRESSION_RATIO}"
    echo ""
}

check_dependencies() {
    log_info "Checking dependencies..."

    # Check Python
    if ! command -v python &> /dev/null; then
        log_error "Python not found. Please install Python 3.9+"
        exit 1
    fi

    # Check PyTorch
    if ! python -c "import torch" &> /dev/null; then
        log_error "PyTorch not found. Install with: pip install torch"
        exit 1
    fi

    # Check CUDA
    if ! python -c "import torch; assert torch.cuda.is_available()" &> /dev/null; then
        log_warning "CUDA not available. Training will run on CPU."
    fi

    # Check GPU count
    GPU_COUNT=$(python -c "import torch; print(torch.cuda.device_count())")
    if [ "$GPU_COUNT" -lt "$GPU_PER_NODE" ]; then
        log_error "Requested ${GPU_PER_NODE} GPUs but only ${GPU_COUNT} available"
        exit 1
    fi

    # Check torchrun
    if ! command -v torchrun &> /dev/null; then
        log_error "torchrun not found. Please install PyTorch 2.0+"
        exit 1
    fi

    log_success "All dependencies satisfied"
}

setup_environment() {
    log_info "Setting up environment..."

    # Set environment variables
    export MASTER_ADDR="${MASTER_ADDR}"
    export MASTER_PORT="${MASTER_PORT}"

    # NCCL settings
    export NCCL_DEBUG=INFO
    export NCCL_BLOCKING_WAIT=1

    # Python settings
    export PYTHONUNBUFFERED=1
    export TORCH_CUDA_ARCH_LIST="8.0;8.6;9.0"  # RTX 4050, RTX 4090, A100

    log_success "Environment configured"
}

launch_training() {
    log_info "Launching distributed training..."

    # Build torchrun command
    TORCHRUN_CMD="torchrun"

    # Multi-node settings
    if [ "$NUM_NODES" -gt 1 ]; then
        TORCHRUN_CMD="${TORCHRUN_CMD} --nnodes=${NUM_NODES}"
        TORCHRUN_CMD="${TORCHRUN_CMD} --nproc_per_node=${GPU_PER_NODE}"
        TORCHRUN_CMD="${TORCHRUN_CMD} --master_addr=${MASTER_ADDR}"
        TORCHRUN_CMD="${TORCHRUN_CMD} --master_port=${MASTER_PORT}"

        # Get node rank from environment or prompt
        if [ -z "$NODE_RANK" ]; then
            read -p "Enter node rank (0-${NUM_NODES}): " NODE_RANK
        fi
        TORCHRUN_CMD="${TORCHRUN_CMD} --node_rank=${NODE_RANK}"
    else
        # Single node
        TORCHRUN_CMD="${TORCHRUN_CMD} --nproc_per_node=${GPU_PER_NODE}"
    fi

    # Python script
    TORCHRUN_CMD="${TORCHRUN_CMD} ${PYTHON_SCRIPT}"

    # Training arguments
    TORCHRUN_CMD="${TORCHRUN_CMD} --batch-size ${BATCH_SIZE}"
    TORCHRUN_CMD="${TORCHRUN_CMD} --epochs ${EPOCHS}"
    TORCHRUN_CMD="${TORCHRUN_CMD} --learning-rate ${LEARNING_RATE}"

    # Feature flags
    if [ "$USE_CRDT" != "true" ]; then
        TORCHRUN_CMD="${TORCHRUN_CMD} --no-crdt"
    fi

    if [ "$USE_AMP" != "true" ]; then
        TORCHRUN_CMD="${TORCHRUN_CMD} --no-amp"
    fi

    log_info "Running: ${TORCHRUN_CMD}"
    echo ""

    # Execute
    eval $TORCHRUN_CMD
}

monitor_training() {
    log_info "Training monitoring commands:"
    echo ""
    echo "  # Watch GPU utilization"
    echo "  watch -n 1 nvidia-smi"
    echo ""
    echo "  # View logs"
    echo "  tail -f /tmp/training_*.log"
    echo ""
    echo "  # Check network connections"
    echo "  netstat -an | grep ${MASTER_PORT}"
    echo ""
}

###############################################################################
# Argument Parsing
###############################################################################

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --nodes)
                NUM_NODES="$2"
                shift 2
                ;;
            --gpu-per-node)
                GPU_PER_NODE="$2"
                shift 2
                ;;
            --master-addr)
                MASTER_ADDR="$2"
                shift 2
                ;;
            --master-port)
                MASTER_PORT="$2"
                shift 2
                ;;
            --batch-size)
                BATCH_SIZE="$2"
                shift 2
                ;;
            --epochs)
                EPOCHS="$2"
                shift 2
            ;;
            --learning-rate)
                LEARNING_RATE="$2"
                shift 2
                ;;
            --no-crdt)
                USE_CRDT=false
                shift
                ;;
            --no-amp)
                USE_AMP=false
                shift
                ;;
            --compression-ratio)
                COMPRESSION_RATIO="$2"
                shift 2
                ;;
            --script)
                PYTHON_SCRIPT="$2"
                shift 2
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --nodes N              Number of nodes (default: 1)"
                echo "  --gpu-per-node N       GPUs per node (default: 4)"
                echo "  --master-addr ADDR     Master node address (default: localhost)"
                echo "  --master-port PORT     Master port (default: 29500)"
                echo "  --batch-size N         Batch size per GPU (default: 128)"
                echo "  --epochs N             Number of epochs (default: 100)"
                echo "  --learning-rate LR     Learning rate (default: 0.001)"
                echo "  --no-crdt              Disable CRDT synchronization"
                echo "  --no-amp               Disable automatic mixed precision"
                echo "  --compression-ratio R  Gradient compression ratio (default: 0.1)"
                echo "  --script PATH          Python script to run"
                echo "  --help                 Show this help message"
                echo ""
                echo "Examples:"
                echo "  # Single node, 4 GPUs"
                echo "  $0 --gpu-per-node 4"
                echo ""
                echo "  # Multi-node, 4 GPUs per node"
                echo "  $0 --nodes 2 --gpu-per-node 4 --master-addr 192.168.1.1"
                echo ""
                echo "  # Custom training script"
                echo "  $0 --script my_model.py --batch-size 256"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
}

###############################################################################
# Main Execution
###############################################################################

main() {
    print_banner

    # Parse arguments
    parse_arguments "$@"

    # Print configuration
    print_config

    # Check dependencies
    check_dependencies

    # Setup environment
    setup_environment

    # Show monitoring commands
    monitor_training

    # Prompt for confirmation
    read -p "Start training? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Launch training
        launch_training
    else
        log_info "Training cancelled by user"
        exit 0
    fi
}

# Run main function
main "$@"
