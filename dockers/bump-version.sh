#!/bin/bash

# Path to the script file that needs version bump
FILE_PATH="src/version.py"

# Function to check if the working tree is clean
check_clean_working_tree() {
    if ! git diff-index --quiet HEAD --; then
        echo "Working tree is not clean. Please commit or stash your changes before running this script."
        exit 1
    fi
}

# Function to bump the version number
bump_version() {
    local current_version=$(grep -oP '__version__ = "\K[0-9]+\.[0-9]+\.[0-9]+' "$FILE_PATH")
    if [[ -z "$current_version" ]]; then
        echo "Current version not found in $FILE_PATH."
        exit 1
    fi
    
    # Split the version into array [major, minor, patch]
    IFS='.' read -r -a version_parts <<< "$current_version"
    
    # Increment the patch version
    version_parts[2]=$((version_parts[2]+1))
    
    # Join the version parts back together
    local new_version="${version_parts[0]}.${version_parts[1]}.${version_parts[2]}"
    
    # Replace the version in the file with the new version using sed
    sed -i "s/\"$current_version\"/\"$new_version\"/" "$FILE_PATH"
    
    echo "Version bumped from $current_version to $new_version."
}

# Function to commit the change
commit_version_bump() {
    local current_version=$(grep -oP '__version__ = "\K[0-9]+\.[0-9]+\.[0-9]+' "$FILE_PATH")
    
    # Add the file to the staging area
    git add "$FILE_PATH"
    
    # Commit the change with a message
    git commit -m "bump version $current_version"
    
    echo "Version $current_version committed."
}

# if have --no-commit flag
if [ "$1" == "--no-commit" ]; then
    bump_version
else
    # Main script execution
    check_clean_working_tree
    bump_version
    commit_version_bump
fi