#!/usr/bin/env python3
"""
Cocotb Testbench Log Parser
Extracts and analyzes test case information from cocotb logs
"""

import re
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import List, Dict, Optional
import argparse
import json


@dataclass
class TestCase:
    test_number: int
    instruction_type: Optional[str] = None
    instruction_name: Optional[str] = None
    rd: Optional[int] = None
    rs1: Optional[int] = None
    rs2: Optional[int] = None
    immediate: Optional[int] = None
    instruction_binary: Optional[str] = None
    pre_rd: Optional[int] = None
    pre_rs1: Optional[int] = None
    pre_rs2: Optional[int] = None
    actual_rd: Optional[int] = None
    actual_rs1: Optional[int] = None
    actual_rs2: Optional[int] = None
    expected_rd: Optional[int] = None
    success: bool = False
    overflow: bool = False
    illegal_instruction: bool = False
    raw_text: str = ""


class CocotbLogParser:
    def __init__(self):
        self.test_cases: List[TestCase] = []
        self.stats = {
            'total_tests': 0,
            'successes': 0,
            'failures': 0,
            'overflows': 0,
            'illegal_instructions': 0,
            'instruction_counts': Counter(),
            'instruction_type_counts': Counter(),
            'register_usage': Counter(),
            'rd_usage': Counter(),
            'rs1_usage': Counter(),
            'rs2_usage': Counter(),
            'immediate_values': Counter(),
            'immediate_ranges': Counter(),
            'register_value_ranges': Counter(),
            'pre_register_values': Counter(),
            'actual_register_values': Counter(),
            # NEW: Specific range tracking for register values
            'pre_register_value_ranges': Counter(),
            'actual_register_value_ranges': Counter(),
            'pre_rd_value_ranges': Counter(),
            'pre_rs1_value_ranges': Counter(),
            'pre_rs2_value_ranges': Counter(),
            'actual_rd_value_ranges': Counter(),
            'actual_rs1_value_ranges': Counter(),
            'actual_rs2_value_ranges': Counter(),
            # NEW: Specific value tracking by register type
            'pre_rd_values': Counter(),
            'pre_rs1_values': Counter(),
            'pre_rs2_values': Counter(),
            'actual_rd_values': Counter(),
            'actual_rs1_values': Counter(),
            'actual_rs2_values': Counter()
        }

    def parse_log_file(self, filename: str) -> None:
        """Parse a log file and extract test cases"""
        with open(filename, 'r') as f:
            content = f.read()
        
        # Split into individual test cases
        test_blocks = re.split(r'Test \d+', content)[1:]  # Skip first empty split
        test_numbers = re.findall(r'Test (\d+)', content)
        
        for i, (test_num, block) in enumerate(zip(test_numbers, test_blocks)):
            self.parse_test_case(int(test_num), block)

    def parse_test_case(self, test_number: int, block: str) -> None:
        """Parse a single test case block"""
        test_case = TestCase(test_number=test_number, raw_text=block.strip())
        
        # Extract instruction type
        type_match = re.search(r'Instruction type:\s*(\S+)', block)
        if type_match:
            test_case.instruction_type = type_match.group(1)
        
        # Extract instruction name
        name_match = re.search(r'Name:\s*(\S+)', block)
        if name_match:
            test_case.instruction_name = name_match.group(1)
        
        # Extract registers - look in multiple locations
        reg_match = re.search(r'Registers:\s*(.+)', block)
        if reg_match:
            reg_line = reg_match.group(1)
            
            # Parse rd, rs1, rs2
            rd_match = re.search(r'rd=(-?\d+)', reg_line)
            rs1_match = re.search(r'rs1=(-?\d+)', reg_line)
            rs2_match = re.search(r'rs2=(-?\d+)', reg_line)
            imm_match = re.search(r'imm=(-?\d+)', reg_line)
            
            if rd_match:
                test_case.rd = int(rd_match.group(1))
            if rs1_match:
                test_case.rs1 = int(rs1_match.group(1))
            if rs2_match:
                test_case.rs2 = int(rs2_match.group(1))
            if imm_match:
                test_case.immediate = int(imm_match.group(1))
        
        # Look for immediate values in other locations if not found yet
        if test_case.immediate is None:
            # Look for immediate in different formats
            imm_patterns = [
                r'immediate:\s*(-?\d+)',
                r'imm:\s*(-?\d+)', 
                r'immediate\s*=\s*(-?\d+)',
                r'imm\s*=\s*(-?\d+)',
                r'Immediate:\s*(-?\d+)',
                r'IMM:\s*(-?\d+)'
            ]
            
            for pattern in imm_patterns:
                imm_match = re.search(pattern, block, re.IGNORECASE)
                if imm_match:
                    test_case.immediate = int(imm_match.group(1))
                    break
        
        # Extract instruction binary
        instr_match = re.search(r'Instruction:\s*([01]+)', block)
        if instr_match:
            test_case.instruction_binary = instr_match.group(1)
        
        # Extract pre-instruction values
        pre_match = re.search(r'Pre-instruction:\s*(.+)', block)
        if pre_match:
            pre_line = pre_match.group(1)
            pre_rd = re.search(r'rd=(-?\d+)', pre_line)
            pre_rs1 = re.search(r'rs1=(-?\d+)', pre_line)
            pre_rs2 = re.search(r'rs2=(-?\d+)', pre_line)
            
            if pre_rd:
                test_case.pre_rd = int(pre_rd.group(1))
            if pre_rs1:
                test_case.pre_rs1 = int(pre_rs1.group(1))
            if pre_rs2:
                test_case.pre_rs2 = int(pre_rs2.group(1))
        
        # Extract actual values
        actual_match = re.search(r'Actual:\s*(.+)', block)
        if actual_match:
            actual_line = actual_match.group(1)
            act_rd = re.search(r'rd=(-?\d+)', actual_line)
            act_rs1 = re.search(r'rs1=(-?\d+)', actual_line)
            act_rs2 = re.search(r'rs2=(-?\d+)', actual_line)
            
            if act_rd:
                test_case.actual_rd = int(act_rd.group(1))
            if act_rs1:
                test_case.actual_rs1 = int(act_rs1.group(1))
            if act_rs2:
                test_case.actual_rs2 = int(act_rs2.group(1))
        
        # Extract expected result (might be "overflow" instead of a number)
        expected_match = re.search(r'Expected rd:\s*(-?\d+)', block)
        overflow_match = re.search(r'Expected rd:\s*overflow', block, re.IGNORECASE)
        
        if expected_match:
            test_case.expected_rd = int(expected_match.group(1))
        elif overflow_match:
            test_case.overflow = True
        
        # Check for overflow status
        if not test_case.overflow:
            test_case.overflow = 'overflow' in block.lower()
        
        # Check for illegal instruction
        test_case.illegal_instruction = 'illegal' in block.lower()
        
        # Determine success - FIXED LOGIC:
        # A test is successful if:
        # 1. It explicitly says "Success!" OR
        # 2. It has an expected overflow and overflow occurred OR  
        # 3. The actual result matches the expected result (when not overflow)
        explicit_success = 'Success!' in block
        overflow_success = test_case.overflow and ('overflow' in block.lower() or overflow_match)
        
        # Check if actual matches expected (for non-overflow cases)
        value_match_success = False
        if (not test_case.overflow and 
            test_case.expected_rd is not None and 
            test_case.actual_rd is not None):
            value_match_success = test_case.expected_rd == test_case.actual_rd
        
        test_case.success = explicit_success or overflow_success or value_match_success
        
        self.test_cases.append(test_case)
        self.update_stats(test_case)

    def categorize_value(self, value: int) -> str:
        """Categorize a value into ranges for analysis"""
        if value == 0:
            return "zero"
        elif 1 <= abs(value) <= 2**4:
            return f"±2^4 ({'pos' if value > 0 else 'neg'})"
        elif 2**4 < abs(value) <= 2**8:
            return f"±2^8 ({'pos' if value > 0 else 'neg'})"
        elif 2**8 < abs(value) <= 2**10:
            return f"±2^10 ({'pos' if value > 0 else 'neg'})"
        elif 2**10 < abs(value) <= 2**12:
            return f"±2^12 ({'pos' if value > 0 else 'neg'})"
        elif 2**12 < abs(value) <= 2**16:
            return f"±2^16 ({'pos' if value > 0 else 'neg'})"
        elif 2**16 < abs(value) <= 2**20:
            return f"±2^20 ({'pos' if value > 0 else 'neg'})"
        elif 2**20 < abs(value) <= 2**31:
            return f"±2^31 ({'pos' if value > 0 else 'neg'})"
        else:
            return f"large ({'pos' if value > 0 else 'neg'})"

    def update_stats(self, test_case: TestCase) -> None:
        """Update statistics with information from a test case"""
        self.stats['total_tests'] += 1
        
        if test_case.success:
            self.stats['successes'] += 1
        else:
            self.stats['failures'] += 1
        
        if test_case.overflow:
            self.stats['overflows'] += 1
        
        if test_case.illegal_instruction:
            self.stats['illegal_instructions'] += 1
        
        if test_case.instruction_name:
            self.stats['instruction_counts'][test_case.instruction_name] += 1
        
        if test_case.instruction_type:
            self.stats['instruction_type_counts'][test_case.instruction_type] += 1
        
        # Track register usage
        if test_case.rd is not None:
            self.stats['rd_usage'][test_case.rd] += 1
            self.stats['register_usage'][test_case.rd] += 1
        
        if test_case.rs1 is not None:
            self.stats['rs1_usage'][test_case.rs1] += 1
            self.stats['register_usage'][test_case.rs1] += 1
        
        if test_case.rs2 is not None:
            self.stats['rs2_usage'][test_case.rs2] += 1
            self.stats['register_usage'][test_case.rs2] += 1
        
        # Track immediate values
        if test_case.immediate is not None:
            self.stats['immediate_values'][test_case.immediate] += 1
            # Track immediate ranges
            imm_range = self.categorize_value(test_case.immediate)
            self.stats['immediate_ranges'][imm_range] += 1
        
        # Track pre-instruction register values with detailed range analysis
        if test_case.pre_rd is not None:
            self.stats['pre_register_values'][test_case.pre_rd] += 1
            self.stats['pre_rd_values'][test_case.pre_rd] += 1
            val_range = self.categorize_value(test_case.pre_rd)
            self.stats['register_value_ranges'][val_range] += 1
            self.stats['pre_register_value_ranges'][val_range] += 1
            self.stats['pre_rd_value_ranges'][val_range] += 1
            
        if test_case.pre_rs1 is not None:
            self.stats['pre_register_values'][test_case.pre_rs1] += 1
            self.stats['pre_rs1_values'][test_case.pre_rs1] += 1
            val_range = self.categorize_value(test_case.pre_rs1)
            self.stats['register_value_ranges'][val_range] += 1
            self.stats['pre_register_value_ranges'][val_range] += 1
            self.stats['pre_rs1_value_ranges'][val_range] += 1
            
        if test_case.pre_rs2 is not None:
            self.stats['pre_register_values'][test_case.pre_rs2] += 1
            self.stats['pre_rs2_values'][test_case.pre_rs2] += 1
            val_range = self.categorize_value(test_case.pre_rs2)
            self.stats['register_value_ranges'][val_range] += 1
            self.stats['pre_register_value_ranges'][val_range] += 1
            self.stats['pre_rs2_value_ranges'][val_range] += 1
        
        # Track actual register values with detailed range analysis
        if test_case.actual_rd is not None:
            self.stats['actual_register_values'][test_case.actual_rd] += 1
            self.stats['actual_rd_values'][test_case.actual_rd] += 1
            val_range = self.categorize_value(test_case.actual_rd)
            self.stats['actual_register_value_ranges'][val_range] += 1
            self.stats['actual_rd_value_ranges'][val_range] += 1
            
        if test_case.actual_rs1 is not None:
            self.stats['actual_register_values'][test_case.actual_rs1] += 1
            self.stats['actual_rs1_values'][test_case.actual_rs1] += 1
            val_range = self.categorize_value(test_case.actual_rs1)
            self.stats['actual_register_value_ranges'][val_range] += 1
            self.stats['actual_rs1_value_ranges'][val_range] += 1
            
        if test_case.actual_rs2 is not None:
            self.stats['actual_register_values'][test_case.actual_rs2] += 1
            self.stats['actual_rs2_values'][test_case.actual_rs2] += 1
            val_range = self.categorize_value(test_case.actual_rs2)
            self.stats['actual_register_value_ranges'][val_range] += 1
            self.stats['actual_rs2_value_ranges'][val_range] += 1

    def print_summary(self) -> None:
        """Print a summary of parsed results"""
        print("=" * 60)
        print("COCOTB LOG PARSER SUMMARY")
        print("=" * 60)
        
        print(f"\nTEST RESULTS:")
        print(f"  Total Tests: {self.stats['total_tests']}")
        print(f"  Successes: {self.stats['successes']}")
        print(f"  Failures: {self.stats['failures']}")
        print(f"  Success Rate: {self.stats['successes']/self.stats['total_tests']*100:.1f}%")
        print(f"  Overflows: {self.stats['overflows']} (counted as successes when expected)")
        print(f"  Illegal Instructions: {self.stats['illegal_instructions']}")
        
        print(f"\nINSTRUCTION STATISTICS:")
        print(f"  Most Common Instructions:")
        for instr, count in self.stats['instruction_counts'].most_common(10):
            print(f"    {instr}: {count} times")
        
        print(f"\nINSTRUCTION TYPES:")
        for instr_type, count in self.stats['instruction_type_counts'].most_common():
            print(f"    {instr_type}: {count} times")
        
        print(f"\nREGISTER USAGE:")
        print(f"  Most Used Registers:")
        for reg, count in self.stats['register_usage'].most_common(10):
            print(f"    r{reg}: {count} times")
        
        print(f"\n  Destination Register (rd) Usage:")
        for reg, count in self.stats['rd_usage'].most_common(5):
            print(f"    r{reg}: {count} times")
        
        print(f"\n  Source Register 1 (rs1) Usage:")
        for reg, count in self.stats['rs1_usage'].most_common(5):
            print(f"    r{reg}: {count} times")
        
        print(f"\n  Source Register 2 (rs2) Usage:")
        for reg, count in self.stats['rs2_usage'].most_common(5):
            print(f"    r{reg}: {count} times")
        
        # Print immediate value statistics
        if self.stats['immediate_values']:
            print(f"\nIMMEDIATE VALUE STATISTICS:")
            print(f"  Total instructions with immediates: {sum(self.stats['immediate_values'].values())}")
            print(f"  Most Common Immediate Values:")
            for imm, count in self.stats['immediate_values'].most_common(10):
                print(f"    {imm}: {count} times")
            
            print(f"\n  Immediate Value Ranges:")
            for range_name, count in self.stats['immediate_ranges'].most_common():
                print(f"    {range_name}: {count} times")
        
        # NEW: Print detailed register value statistics
        if self.stats['pre_register_values']:
            print(f"\nPRE-INSTRUCTION REGISTER VALUE STATISTICS:")
            print(f"  Total pre-instruction register values: {sum(self.stats['pre_register_values'].values())}")
            print(f"  Most Common Pre-Instruction Values:")
            for val, count in self.stats['pre_register_values'].most_common(10):
                print(f"    {val}: {count} times")
            
            print(f"\n  Pre-Instruction Value Ranges:")
            for range_name, count in self.stats['pre_register_value_ranges'].most_common():
                print(f"    {range_name}: {count} times")
            
            # Detailed breakdown by register type
            if self.stats['pre_rd_values']:
                print(f"\n  Pre-RD Value Ranges:")
                for range_name, count in self.stats['pre_rd_value_ranges'].most_common():
                    print(f"    {range_name}: {count} times")
            
            if self.stats['pre_rs1_values']:
                print(f"\n  Pre-RS1 Value Ranges:")
                for range_name, count in self.stats['pre_rs1_value_ranges'].most_common():
                    print(f"    {range_name}: {count} times")
                    
            if self.stats['pre_rs2_values']:
                print(f"\n  Pre-RS2 Value Ranges:")
                for range_name, count in self.stats['pre_rs2_value_ranges'].most_common():
                    print(f"    {range_name}: {count} times")
        
        if self.stats['actual_register_values']:
            print(f"\nACTUAL REGISTER VALUE STATISTICS:")
            print(f"  Total actual register values: {sum(self.stats['actual_register_values'].values())}")
            print(f"  Most Common Actual Values:")
            for val, count in self.stats['actual_register_values'].most_common(10):
                print(f"    {val}: {count} times")
            
            print(f"\n  Actual Value Ranges:")
            for range_name, count in self.stats['actual_register_value_ranges'].most_common():
                print(f"    {range_name}: {count} times")
            
            # Detailed breakdown by register type
            if self.stats['actual_rd_values']:
                print(f"\n  Actual RD Value Ranges:")
                for range_name, count in self.stats['actual_rd_value_ranges'].most_common():
                    print(f"    {range_name}: {count} times")
                    
            if self.stats['actual_rs1_values']:
                print(f"\n  Actual RS1 Value Ranges:")
                for range_name, count in self.stats['actual_rs1_value_ranges'].most_common():
                    print(f"    {range_name}: {count} times")
                    
            if self.stats['actual_rs2_values']:
                print(f"\n  Actual RS2 Value Ranges:")
                for range_name, count in self.stats['actual_rs2_value_ranges'].most_common():
                    print(f"    {range_name}: {count} times")

    def get_failed_tests(self) -> List[TestCase]:
        """Return list of failed test cases"""
        return [tc for tc in self.test_cases if not tc.success]

    def get_instruction_analysis(self, instruction_name: str) -> Dict:
        """Get detailed analysis for a specific instruction"""
        matching_tests = [tc for tc in self.test_cases if tc.instruction_name == instruction_name]
        
        return {
            'total_count': len(matching_tests),
            'success_count': sum(1 for tc in matching_tests if tc.success),
            'failure_count': sum(1 for tc in matching_tests if not tc.success),
            'overflow_count': sum(1 for tc in matching_tests if tc.overflow),
            'registers_used': Counter([tc.rd for tc in matching_tests if tc.rd is not None] +
                                    [tc.rs1 for tc in matching_tests if tc.rs1 is not None] +
                                    [tc.rs2 for tc in matching_tests if tc.rs2 is not None]),
            'immediate_values': Counter([tc.immediate for tc in matching_tests if tc.immediate is not None]),
            'pre_register_values': Counter([tc.pre_rd for tc in matching_tests if tc.pre_rd is not None] +
                                         [tc.pre_rs1 for tc in matching_tests if tc.pre_rs1 is not None] +
                                         [tc.pre_rs2 for tc in matching_tests if tc.pre_rs2 is not None]),
            'actual_register_values': Counter([tc.actual_rd for tc in matching_tests if tc.actual_rd is not None] +
                                            [tc.actual_rs1 for tc in matching_tests if tc.actual_rs1 is not None] +
                                            [tc.actual_rs2 for tc in matching_tests if tc.actual_rs2 is not None])
        }

    def export_to_json(self, filename: str) -> None:
        """Export parsed data to JSON"""
        data = {
            'stats': {
                'total_tests': self.stats['total_tests'],
                'successes': self.stats['successes'],
                'failures': self.stats['failures'],
                'overflows': self.stats['overflows'],
                'illegal_instructions': self.stats['illegal_instructions'],
                'instruction_counts': dict(self.stats['instruction_counts']),
                'instruction_type_counts': dict(self.stats['instruction_type_counts']),
                'register_usage': dict(self.stats['register_usage']),
                'rd_usage': dict(self.stats['rd_usage']),
                'rs1_usage': dict(self.stats['rs1_usage']),
                'rs2_usage': dict(self.stats['rs2_usage']),
                'immediate_values': dict(self.stats['immediate_values']),
                'immediate_ranges': dict(self.stats['immediate_ranges']),
                'register_value_ranges': dict(self.stats['register_value_ranges']),
                'pre_register_values': dict(self.stats['pre_register_values']),
                'actual_register_values': dict(self.stats['actual_register_values']),
                'pre_register_value_ranges': dict(self.stats['pre_register_value_ranges']),
                'actual_register_value_ranges': dict(self.stats['actual_register_value_ranges']),
                'pre_rd_value_ranges': dict(self.stats['pre_rd_value_ranges']),
                'pre_rs1_value_ranges': dict(self.stats['pre_rs1_value_ranges']),
                'pre_rs2_value_ranges': dict(self.stats['pre_rs2_value_ranges']),
                'actual_rd_value_ranges': dict(self.stats['actual_rd_value_ranges']),
                'actual_rs1_value_ranges': dict(self.stats['actual_rs1_value_ranges']),
                'actual_rs2_value_ranges': dict(self.stats['actual_rs2_value_ranges']),
                'pre_rd_values': dict(self.stats['pre_rd_values']),
                'pre_rs1_values': dict(self.stats['pre_rs1_values']),
                'pre_rs2_values': dict(self.stats['pre_rs2_values']),
                'actual_rd_values': dict(self.stats['actual_rd_values']),
                'actual_rs1_values': dict(self.stats['actual_rs1_values']),
                'actual_rs2_values': dict(self.stats['actual_rs2_values'])
            },
            'test_cases': [
                {
                    'test_number': tc.test_number,
                    'instruction_type': tc.instruction_type,
                    'instruction_name': tc.instruction_name,
                    'rd': tc.rd,
                    'rs1': tc.rs1,
                    'rs2': tc.rs2,
                    'immediate': tc.immediate,
                    'instruction_binary': tc.instruction_binary,
                    'pre_rd': tc.pre_rd,
                    'pre_rs1': tc.pre_rs1,
                    'pre_rs2': tc.pre_rs2,
                    'actual_rd': tc.actual_rd,
                    'actual_rs1': tc.actual_rs1,
                    'actual_rs2': tc.actual_rs2,
                    'expected_rd': tc.expected_rd,
                    'success': tc.success,
                    'overflow': tc.overflow,
                    'illegal_instruction': tc.illegal_instruction
                } for tc in self.test_cases
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Parse cocotb testbench logs')
    parser.add_argument('logfile', help='Path to the log file to parse')
    parser.add_argument('--export', help='Export results to JSON file')
    parser.add_argument('--analyze', help='Analyze specific instruction')
    parser.add_argument('--failures', action='store_true', help='Show failed test details')
    
    args = parser.parse_args()
    
    log_parser = CocotbLogParser()
    log_parser.parse_log_file(args.logfile)
    log_parser.print_summary()
    
    if args.failures:
        failed_tests = log_parser.get_failed_tests()
        if failed_tests:
            print(f"\nFAILED TESTS ({len(failed_tests)}):")
            for tc in failed_tests:
                print(f"\n  === Test {tc.test_number} FAILED ===")
                print(f"      Instruction: {tc.instruction_name} ({tc.instruction_type})")
                if tc.rd is not None:
                    print(f"      Registers: rd={tc.rd}, rs1={tc.rs1}, rs2={tc.rs2}")
                if tc.immediate is not None:
                    print(f"      Immediate: {tc.immediate}")
                if tc.expected_rd is not None and tc.actual_rd is not None:
                    print(f"      Expected rd: {tc.expected_rd}, Actual rd: {tc.actual_rd}")
                if tc.overflow:
                    print(f"      Status: OVERFLOW")
                if tc.illegal_instruction:
                    print(f"      Status: ILLEGAL INSTRUCTION")
                print(f"      Raw: {tc.raw_text[:200]}...")
        else:
            print(f"\nNo failed tests found!")
    
    if args.analyze:
        analysis = log_parser.get_instruction_analysis(args.analyze)
        print(f"\nANALYSIS FOR '{args.analyze}':")
        print(f"  Total: {analysis['total_count']}")
        print(f"  Success: {analysis['success_count']}")
        print(f"  Failures: {analysis['failure_count']}")
        print(f"  Overflows: {analysis['overflow_count']}")
        print(f"  Registers used: {dict(analysis['registers_used'].most_common(5))}")
        if analysis['immediate_values']:
            print(f"  Immediate values: {dict(analysis['immediate_values'].most_common(5))}")
        if analysis['pre_register_values']:
            print(f"  Pre-register values: {dict(analysis['pre_register_values'].most_common(5))}")
        if analysis['actual_register_values']:
            print(f"  Actual register values: {dict(analysis['actual_register_values'].most_common(5))}")
    
    if args.export:
        log_parser.export_to_json(args.export)
        print(f"\nResults exported to {args.export}")


if __name__ == "__main__":
    main()