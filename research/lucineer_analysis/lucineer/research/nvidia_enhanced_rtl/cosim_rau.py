import cocotb
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb.binary import BinaryValue
from cocotb.utils import get_sim_time
from cocotb.result import TestFailure
from cocotb.scoreboard import Scoreboard
from cocotb.coverage import CoverPoint, CoverCross

# Python model of RAU
class RAUModel:
    def __init__(self):
        self.result = 0

    def execute(self, a, b, op):
        if op == 0:  # ADD
            self.result = a + b
        elif op == 1:  # SUB
            self.result = a - b
        elif op == 2:  # MUL
            self.result = a * b
        elif op == 3:  # DIV
            if b != 0:
                self.result = a // b
            else:
                self.result = 0
        return self.result

# Scoreboard for comparison
class RAUScoreboard(Scoreboard):
    def __init__(self, dut):
        super().__init__()
        self.model = RAUModel()
        self.dut = dut
        self.expectation = []
        self.result = []

    def compare(self, transaction):
        model_result = self.model.execute(transaction['a'], transaction['b'], transaction['op'])
        dut_result = self.dut.result.value.integer
        self.expectation.append(model_result)
        self.result.append(dut_result)

    def check(self):
        for exp, res in zip(self.expectation, self.result):
            if exp != res:
                raise TestFailure(f"Expected {exp}, got {res}")

# Coverage database generation
class RAUCoverage:
    def __init__(self):
        self.cp_op = CoverPoint("op", xf = lambda x: x['op'])
        self.cp_a = CoverPoint("a", xf = lambda x: x['a'])
        self.cp_b = CoverPoint("b", xf = lambda x: x['b'])
        self.cc_ab = CoverCross("a", "b", xf = lambda x: (x['a'], x['b']))

    def sample(self, transaction):
        self.cp_op.sample(transaction)
        self.cp_a.sample(transaction)
        self.cp_b.sample(transaction)
        self.cc_ab.sample(transaction)

# Test cases as coroutines
@cocotb.test()
async def test_rau(dut):
    rau_model = RAUModel()
    scoreboard = RAUScoreboard(dut)
    coverage = RAUCoverage()

    # Reset the DUT
    await RisingEdge(dut.clk)
    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0

    # Test cases
    test_cases = [
        {'a': 10, 'b': 5, 'op': 0},  # ADD
        {'a': 10, 'b': 5, 'op': 1},  # SUB
        {'a': 10, 'b': 5, 'op': 2},  # MUL
        {'a': 10, 'b': 5, 'op': 3},  # DIV
        {'a': 10, 'b': 0, 'op': 3},  # DIV by zero
    ]

    for transaction in test_cases:
        # Drive stimuli from Python
        dut.a.value = transaction['a']
        dut.b.value = transaction['b']
        dut.op.value = transaction['op']

        # Wait for the result
        await RisingEdge(dut.result_valid)

        # Compare the result
        scoreboard.compare(transaction)

        # Sample coverage
        coverage.sample(transaction)

    # Check the scoreboard
    scoreboard.check()

    # Print coverage report
    print("Coverage report:")
    print("  op:", coverage.cp_op.coverage)
    print("  a:", coverage.cp_a.coverage)
    print("  b:", coverage.cp_b.coverage)
    print("  ab:", coverage.cc_ab.coverage)