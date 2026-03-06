import json
import re
import sys
from pathlib import Path

def process_jsonl_file(input_file, output_file=None):
    """
    Fix JSON errors in a JSONL file.
    
    Args:
        input_file: Path to input JSONL file
        output_file: Path to output file (default: input_file with '_fixed' suffix)
    
    Returns:
        bool: True if all lines were fixed successfully, False otherwise
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"ERROR: File not found: {input_file}")
        return False
    
    # Default output filename
    if output_file is None:
        output_file = str(input_path.parent / (input_path.stem + '_fixed.txt'))
    
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print("="*70)
    
    # Read all lines  
    lines = open(input_file, 'r', encoding='utf-8', errors='replace').readlines()

    valid_lines = []
    stats = {'valid': 0, 'fixed': 0, 'dropped': 0}

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        # Try parsing original
        try:
            obj = json.loads(line)
            valid_lines.append(json.dumps(obj, ensure_ascii=False, separators=(',', ': ')))
            stats['valid'] += 1
            print(f"Line {line_num:2d}: OK Valid")
            continue
        except:
            pass
        
        # Apply fixes
        fixed = line
        
        # Fix 1: Triple quotes in arrays
        fixed = re.sub(r',\s*"""\s*,', r', "", ', fixed)
        fixed = re.sub(r'\[\s*"""\s*,', r'["", ', fixed)
        fixed = re.sub(r',\s*"""\s*\]', r', ""]', fixed)
        
        # Fix 2: Attribute patterns in tokens (like "rowspan="2"" -> "rowspan=2")
        fixed = re.sub(r'"([^"]+?)="(\d+)""', r'"\1=\2"', fixed)
        
        # Fix 3: Escape quotes in HTML attributes within the "gt" field
        # Find the "gt" field and escape HTML attribute quotes
        gt_match = re.search(r'"gt":\s*"', fixed)
        if gt_match:
            gt_start = gt_match.end()
            
            # Find the end of the gt string (look for unescaped closing quote followed by })
            # We need to be careful here
            remaining = fixed[gt_start:]
            
            # Strategy: Extract the HTML content and properly escape it
            # The gt field is the last field in the JSON, so it goes to near the end
            # Pattern: "gt": "HTML CONTENT"}
            
            # Split at the "gt": " part
            before_gt = fixed[:gt_start]
            after_gt_start = fixed[gt_start:]
            
            # Find where the gt field ends (should be "})
            # Look for the pattern: unescaped quote, brace, end
            # This is tricky because we need to find the LAST closing
            
            # Simpler approach: Extract everything after "gt": and before the final }
            # The gt field should end with "}
            if after_gt_start.endswith('}"'):
                gt_content = after_gt_start[:-2]
            elif after_gt_start.endswith('}'):
                # Find the last quote before the final }  
                last_quote = after_gt_start.rfind('"', 0, -1)
                if last_quote != -1:
                    gt_content = after_gt_start[:last_quote]
                    after_gt = after_gt_start[last_quote:]
                else:
                    gt_content = after_gt_start
                    after_gt = ""
            else:
                gt_content = after_gt_start
                after_gt = ""
            
            # Now escape quotes in HTML attributes (rowspan="X", colspan="X", etc.)
            # Pattern: attribute="value" should become attribute=\"value\"
            escaped_gt = re.sub(r'([a-zA-Z]+)="([^"]*)"', r'\1=\\"\2\\"', gt_content)
            
            # Rebuild the line
            if after_gt_start.endswith('}"'):
                fixed = before_gt + escaped_gt + '}"'
            elif after_gt_start.endswith('}'):
                fixed = before_gt + escaped_gt + '"}'
            else:
                fixed = before_gt + escaped_gt + after_gt
        
        # Try parsing
        try:
            obj = json.loads(fixed)
            valid_lines.append(json.dumps(obj, ensure_ascii=False, separators=(',', ': ')))
            stats['fixed'] += 1
            print(f"Line {line_num:2d}: OK Fixed")
            continue
        except json.JSONDecodeError as e:
            stats['dropped'] += 1
            print(f"Line {line_num:2d}: XX Dropped - {str(e)[:50]}")

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Valid (no changes):  {stats['valid']}")
    print(f"Fixed:               {stats['fixed']}")
    print(f"Dropped:             {stats['dropped']}")
    print(f"Total output:        {len(valid_lines)} / {len([l for l in lines if l.strip()])}")

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in valid_lines:
            f.write(line + '\n')

    print(f"\n>> Output saved to: {output_file}")

    if stats['dropped'] == 0:
        print("\n*** SUCCESS! ALL LINES FIXED! ***")
        
        # Ask about replacement
        response = input("\nReplace original file with fixed version? (y/n): ").strip().lower()
        if response == 'y':
            import shutil
            backup = str(Path(input_file).parent / (Path(input_file).stem + '_backup.txt'))
            shutil.copy2(input_file, backup)
            print(f">> Backup: {backup}")
            shutil.copy2(output_file, input_file)
            print(f">> Original updated!")
        
        return True
    else:
        print(f"\n⚠ {stats['dropped']} line(s) could not be fixed.")
        return False


def main():
    """Main entry point with command-line argument support."""
    
    # Default file paths
    default_input = r"c:\Users\Anurag Katkar\Documents\Programs\Work\aws-textract\aws-to-paddle-dataset\train.txt"
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        # Interactive mode or use defaults
        print("JSON JSONL Fixer - Fix malformed JSON in line-delimited files")
        print("="*70)
        print("\nUsage:")
        print("  python fix_json_complete.py <input_file> [output_file]")
        print("\nExamples:")
        print("  python fix_json_complete.py data.txt")
        print("  python fix_json_complete.py data.txt data_clean.txt")
        print("  python fix_json_complete.py")
        print()
        
        user_input = input("Enter input file path (or press Enter for default): ").strip()
        
        if user_input:
            input_file = user_input
            output_file = None
        else:
            input_file = default_input
            output_file = None
    
    # Process the file
    print()
    success = process_jsonl_file(input_file, output_file)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
