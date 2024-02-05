import argparse
import glob
import re
import os

def find_and_update_hcl_files(limit):
    updated_files_count = 0
    for hcl_file in glob.glob('terragrunt/**/*.hcl', recursive=True):
        if updated_files_count >= limit:
            break

        with open(hcl_file, 'r+') as file:
            content = file.read()
            new_content, replacements = re.subn(r'\b(\d+)\b', lambda x: str(int(x.group(0)) + 1), content)
            if replacements == 0:  # No number found, add number 1
                new_content = '1' if not content else content + '\n1'
            file.seek(0)
            file.write(new_content)
            file.truncate()
            updated_files_count += 1
            print(f"Updated {hcl_file}")

    print(f"Total files updated: {updated_files_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update numbers in .hcl files")
    parser.add_argument('limit', type=int, help="Number of .hcl files to update")
    args = parser.parse_args()

    find_and_update_hcl_files(args.limit)
