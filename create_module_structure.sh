#!/bin/bash

# Bash script to create the file structure for the futuristic_psychologists Odoo module
# This script creates only the directories and empty files, not the content

# Set the module name
MODULE_NAME="futuristic_psychologists"

echo "Creating file structure for Odoo 17 module: $MODULE_NAME"

# Create the main module directory
mkdir -p "$MODULE_NAME"

# Navigate to the module directory
cd "$MODULE_NAME"

# Create main module files
touch __init__.py
touch __manifest__.py
touch README.md

# Create models directory and files
mkdir -p models
touch models/__init__.py
touch models/clinical_psychologist_screening.py
touch models/clinical_psychologist_session.py
touch models/psychometric_assessment.py
touch models/advice_clinical_psychologist.py
touch models/discharge_summary.py

# Create views directory and files
mkdir -p views
touch views/clinical_psychologist_screening_views.xml
touch views/clinical_psychologist_session_views.xml
touch views/psychometric_assessment_views.xml
touch views/advice_clinical_psychologist_views.xml
touch views/discharge_summary_views.xml
touch views/menu_views.xml
touch views/session_extension.xml

# Create security directory and files
mkdir -p security
touch security/security.xml
touch security/ir.model.access.csv

# Create data directory and files
mkdir -p data
touch data/data.xml

# Create static directory structure (optional for future assets)
mkdir -p static/description
touch static/description/icon.png
mkdir -p static/src/css
mkdir -p static/src/js
mkdir -p static/src/xml

# Create demo directory (optional)
mkdir -p demo
touch demo/demo_data.xml

# Create wizard directory (optional for future wizards)
mkdir -p wizard

# Create report directory (optional for future reports)
mkdir -p report

# Create tests directory (optional for unit tests)
mkdir -p tests
touch tests/__init__.py
touch tests/test_clinical_psychology.py

# Create i18n directory for translations
mkdir -p i18n

echo "File structure created successfully!"
echo ""
echo "Created directory structure:"
echo "📁 $MODULE_NAME/"
echo "├── 📄 __init__.py"
echo "├── 📄 __manifest__.py"
echo "├── 📄 README.md"
echo "├── 📁 models/"
echo "│   ├── 📄 __init__.py"
echo "│   ├── 📄 clinical_psychologist_screening.py"
echo "│   ├── 📄 clinical_psychologist_session.py"
echo "│   ├── 📄 psychometric_assessment.py"
echo "│   ├── 📄 advice_clinical_psychologist.py"
echo "│   └── 📄 discharge_summary.py"
echo "├── 📁 views/"
echo "│   ├── 📄 clinical_psychologist_screening_views.xml"
echo "│   ├── 📄 clinical_psychologist_session_views.xml"
echo "│   ├── 📄 psychometric_assessment_views.xml"
echo "│   ├── 📄 advice_clinical_psychologist_views.xml"
echo "│   ├── 📄 discharge_summary_views.xml"
echo "│   ├── 📄 menu_views.xml"
echo "│   └── 📄 session_extension.xml"
echo "├── 📁 security/"
echo "│   ├── 📄 security.xml"
echo "│   └── 📄 ir.model.access.csv"
echo "├── 📁 data/"
echo "│   └── 📄 data.xml"
echo "├── 📁 static/"
echo "│   ├── 📁 description/"
echo "│   │   └── 📄 icon.png"
echo "│   └── 📁 src/"
echo "│       ├── 📁 css/"
echo "│       ├── 📁 js/"
echo "│       └── 📁 xml/"
echo "├── 📁 demo/"
echo "│   └── 📄 demo_data.xml"
echo "├── 📁 wizard/"
echo "├── 📁 report/"
echo "├── 📁 tests/"
echo "│   ├── 📄 __init__.py"
echo "│   └── 📄 test_clinical_psychology.py"
echo "└── 📁 i18n/"
echo ""
echo "✅ All files and directories have been created!"
echo "📝 You can now add your code content to the respective files."
echo ""
echo "To make this script executable, run:"
echo "chmod +x create_module_structure.sh"
echo ""
echo "To execute this script, run:"
echo "./create_module_structure.sh"