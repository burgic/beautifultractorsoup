#!/bin/bash

# chmod +x setup.sh

# Step 1: Create a virtual environment
# python3 -m venv myenv

# Step 2: Activate the virtual environment
source myenv/bin/activate

# Step 3: Upgrade pip
pip3 install --upgrade pip

# Step 4: Install dependencies
pip3 install -r requirements.txt

# Step 5: Notify the user
echo "Virtual environment setup complete. To activate it, run 'source myenv/bin/activate'"
