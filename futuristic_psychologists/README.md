# Clinical Psychology Management Module for Odoo 17

This module provides comprehensive management for clinical psychology operations in healthcare institutions.

## Features

### 1. Clinical Psychology Screening
- Patient screening management for both inpatient and outpatient cases
- Integration with Sarathy AI for enhanced documentation
- Comprehensive notes and tracking capabilities

### 2. Clinical Psychology Sessions
- Complete session management with check-in/check-out functionality
- Session targets, objectives, and outcomes tracking
- Home/work assignments management
- Follow-up planning and scheduling
- Integration with various consultation types (clinic, virtual, home-based)

### 3. Psychometric Assessments
- Standardized assessment creation and management
- Psychiatrist assignment and oversight
- Detailed documentation and reporting

### 4. Advice to Clinical Psychologist
- Professional advice and recommendation system
- Follow-up type management
- Patient-specific guidance documentation

### 5. Discharge Summary
- Multi-level approval workflow (Clinical Psychologist, Psychiatrist, Registrar)
- Comprehensive discharge documentation
- State management and tracking

## Key Improvements in Odoo 17 Migration

### Technical Updates
- **Removed deprecated `attrs` and `states`**: Replaced with modern `invisible`, `readonly`, `required` attributes
- **Updated field visibility**: Used `column_invisible` instead of `invisible` for conditional field display
- **Modern widget usage**: Updated to Odoo 17 compatible widgets
- **Security enhancements**: Implemented proper access control with user groups

### Functional Enhancements
- **Improved user interface**: Modern, responsive design with better user experience
- **Enhanced tracking**: Full mail thread integration for better communication
- **Better search capabilities**: Advanced filtering and grouping options
- **Workflow optimization**: Streamlined approval processes and state management

## Installation

1. Copy the module to your Odoo addons directory
2. Update the addons list in Odoo
3. Install the "Clinical Psychology Management" module
4. Configure user access rights as needed

## Dependencies

- base
- mail
- web

## Security Groups

- **Clinical Psychology User**: Basic access to all clinical psychology features
- **Clinical Psychology Manager**: Full management capabilities
- **Discharge Summary Approvers**: 
  - Clinical Psychologist approval rights
  - Psychiatrist approval rights
  - Registrar approval rights

## Usage

### Creating a Screening
1. Navigate to Clinical Psychology > Screening
2. Click Create
3. Select patient type (IP/OP) and patient
4. Fill in screening notes using the integrated Sarathy AI interface
5. Save the record

### Managing Sessions
1. Go to Clinical Psychology > Session
2. Create a new session record
3. Use Check In/Check Out buttons to track session timing
4. Document session objectives, outcomes, and assignments
5. Complete the session when finished

### Discharge Process
1. Create a discharge summary
2. Confirm the summary to start the approval process
3. Each approver (Clinical Psychologist, Psychiatrist, Registrar) approves in sequence
4. Summary automatically moves to approved state when all approvals are complete

## Support

For technical support or feature requests, please contact your system administrator or the module maintainer.

## License

This module is licensed under LGPL-3.