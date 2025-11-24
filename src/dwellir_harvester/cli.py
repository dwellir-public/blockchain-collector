import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

try:
    from .core import collect_all, bundled_schema_path, load_collectors, run_collector
except ImportError:
    from core import collect_all, bundled_schema_path, load_collectors, run_collector

def build_parser() -> argparse.ArgumentParser:
    """Build the command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="dwellir-harvester",
        description="Collect blockchain node metadata into a JSON file."
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="cmd", required=True)
    
    # 'collect' command
    collect_parser = subparsers.add_parser(
        "collect",
        help="Run one or more collectors and output the results."
    )
    collect_parser.add_argument(
        "collectors",
        nargs="+",
        help="One or more collector names to run (e.g., dummychain system)."
    )
    collect_parser.add_argument(
        "--schema",
        help="Path to JSON Schema file (defaults to bundled schema).",
        default=None
    )
    collect_parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout).",
        type=Path,
        default=None
    )
    collect_parser.add_argument(
        "--no-validate",
        action="store_false",
        dest="validate",
        help="Disable schema validation of the output."
    )
    collect_parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output with detailed error information."
    )
    
    return parser

def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    parser = build_parser()
    parsed_args = parser.parse_args(args)
    
    if parsed_args.cmd == "collect":
        try:
            # Get the schema path (use bundled schema if not specified)
            schema_path = parsed_args.schema or str(bundled_schema_path())
            
            # Load all available collectors
            all_collectors = load_collectors()
            
            # Filter to only the requested collectors
            collectors = []
            for name in parsed_args.collectors:
                if name not in all_collectors:
                    print(f"Warning: Unknown collector '{name}', skipping", file=sys.stderr)
                    continue
                collectors.append(all_collectors[name])
            
            if not collectors:
                print("Error: No valid collectors specified", file=sys.stderr)
                return 1
                
            # Run the collectors
            result = collect_all(
                [c.NAME for c in collectors],
                schema_path=schema_path,
                validate=getattr(parsed_args, 'validate', True),  # Use getattr for backward compatibility
                debug=parsed_args.debug
            )
            
            # Output the result
            output = json.dumps(result, indent=2)
            
            if parsed_args.output:
                parsed_args.output.write_text(output)
                print(f"Results written to {parsed_args.output}")
            else:
                print(output)
                
            return 0
                
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            if parsed_args.debug:  # Show traceback in debug mode
                import traceback
                traceback.print_exc()
            return 1
    
    return 0