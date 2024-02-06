#!/usr/bin/env python

import os
import argparse
import json

# Data for testing purposes
# paths = [
#   # Changed terraform module
#   "terraform/module2/main.tf",
#   # Changed terragrunt module (_envcommon)
#   "terragrunt/_envcommon/module1.hcl",
#   # Changed terragrunt module
#   "terragrunt/account2/account.hcl",
#   "terragrunt/account2/region1/region.hcl",
#   "terragrunt/account2/region1/env-staging/env.hcl",
#   # Changed terragrunt file
#   "terragrunt/account2/region1/env-staging/layer1/terragrunt.hcl",
# ] 

def find_affected_modules(repository_dir: str, changed_modules: list):
    affected_modules = []
    for root, dirs, files in os.walk(f"{repository_dir}/terragrunt"):
        for module in changed_modules:
            if module in dirs:
                # Change path to relative path
                affected_modules.append(os.path.relpath(os.path.join(root, module), repository_dir))
    return affected_modules

def filter_paths(paths):
    # Sort paths to ensure parent paths are considered first
    paths_sorted = sorted(paths, key=lambda x: x.count('/'))

    filtered_paths = []
    for path in paths_sorted:
        # Check if current path is a subpath of any path in filtered_paths
        if not any(path.startswith(parent_path + '/') for parent_path in filtered_paths):
            filtered_paths.append(path)

    return filtered_paths
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse paths")
    parser.add_argument("paths", nargs="*", help="Paths to parse")
    args = parser.parse_args()

    paths = args.paths

    if not paths:
        print("No paths to parse")
        exit(0)

    changed_tf_modules = []
    changed_hcl_folders = []
    changed_envcommon_modules = []
    changed_terragrunt_folders = []
    
    for path in paths:
        if path.endswith("terragrunt.hcl"):
            # If terragrunt.hcl changed, return the path to the folder containing the terragrunt.hcl file
            changed_terragrunt_folders.append(os.path.dirname(path))
        elif path.endswith(".hcl"):
            # If any other .hcl file changed, exept in _envcommon folder, return the paths of subfolders of the folder containing the .hcl file. E.x. file accounts.hcl, region.hcl, etc.
            if "_envcommon" in path:
                # Get the name of the file without extension
                changed_envcommon_modules.append(os.path.basename(path).split(".")[0])
            else:
                changed_hcl_folders.append(os.path.dirname(path))
        elif path.endswith(".tf"):
            # If .tf file changed, return the paths of folders which names contains name of the folder contains the .tf file. E.x. for module1/main.tf its module1
            # Get the name of the folder containing the .tf file
            changed_tf_modules.append(os.path.dirname(path).split("/")[-1])
        else:
            print(f"Unknown file type: {path}")
            exit(1)
    affected_tg_modules = find_affected_modules(os.getcwd(), changed_tf_modules + changed_envcommon_modules)
    
    changed_modules = filter_paths(affected_tg_modules + changed_terragrunt_folders + changed_hcl_folders)
    # print("Changed terragrunt folders: ", changed_terragrunt_folders)
    # print("Changed hcl folders: ", changed_hcl_folders)
    # print("Changed envcommon modules: ", changed_envcommon_modules)
    # print("Changed tf modules: ", changed_tf_modules)
    print("Changed modules: ", changed_modules)
    # Generate fromJSON output, to use matrix strategy in the workflow
    changed_modules_json = json.dumps(changed_modules)
    try:
      with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
          print(f'CHANGED_FOLDERS={changed_modules_json}', file=fh)
    except KeyError:
      print("GITHUB_OUTPUT environment variable not set. Exiting.")
      exit(1)