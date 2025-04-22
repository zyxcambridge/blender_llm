# SPDX-FileCopyrightText: 2023 Blender Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
AI Assistant Configuration

This file contains configuration settings for the AI Assistant functionality.
It stores API keys and other settings needed for AI services integration.
"""

import os
import sys

# Google API Key for AI services
GOOGLE_API_KEY = "AIzaSyC5zCgXXwCNbUmbQR_phRtmciRSBrCcDqg"

# Set environment variable for other modules to access
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Print debug information during startup
print("\n==== AI Assistant Configuration Loaded ====\n", flush=True)
print(f"Google API Key configured: {GOOGLE_API_KEY[:5]}...{GOOGLE_API_KEY[-5:]}\n", flush=True)

# Function to get API key


def get_google_api_key():
    """Returns the configured Google API key"""
    return GOOGLE_API_KEY
