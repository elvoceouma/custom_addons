# FuturisticTech Medical

[![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0.html)
![Odoo Version](https://img.shields.io/badge/Odoo-17.0-blue)
![Stage](https://img.shields.io/badge/Stage-Production%2FStable-green.svg)

## Overview

Comprehensive hospital management system for Odoo 17, providing end-to-end healthcare facility management capabilities.

## Features

- 🏥 Hospital Management
- 👨‍⚕️ Doctor Management
- 👨‍👩‍👧‍👦 Patient Management
- 📅 Appointment System
- 💊 Pharmacy Management
- 💰 Billing Integration

## Quick Links

- [Dependencies](#dependencies)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Development](#development)
- [API Reference](#api-reference)
- [Support](#support)

## Dependencies

```python
{
    'depends': [
        'base',
        'mail',
        'hr',
        'product',
        'account',
    ],
}
```

## Installation

```bash
git clone https://github.com/futuristictech/medical.git
mv medical /path/to/odoo/addons/
service odoo restart
```

## Configuration

### Initial Setup

```python
# Create hospital profile
hospital = env['medical.hospital'].create({
    'name': 'General Hospital',
    'registration_number': 'REG123',
    'license_number': 'LIC456',
})

# Configure departments
department = env['medical.department'].create({
    'name': 'Cardiology',
    'code': 'CARD',
    'hospital_id': hospital.id,
})

# Setup doctors
doctor = env['medical.doctor'].create({
    'employee_id': employee.id,
    'department_id': department.id,
    'specialization': 'Cardiologist',
    'license_number': 'DOC789',
})
```

## Usage

### Hospital Management

```python
# Create new hospital
hospital = self.env['medical.hospital'].create({
    'partner_id': partner.id,
    'registration_number': 'REG123',
    'license_number': 'LIC456',
})

# Add department
department = self.env['medical.department'].create({
    'name': 'Cardiology',
    'code': 'CARD',
    'hospital_id': hospital.id,
    'head_doctor_id': doctor.id,
})

# Search hospitals
hospitals = self.env['medical.hospital'].search([
    ('registration_number', '=', 'REG123'),
    ('active', '=', True)
])
```

### Patient Management

```python
# Register new patient
patient = self.env['medical.patient'].create({
    'partner_id': partner.id,
    'registration_number': 'PAT123',
    'blood_group': 'A+',
    'emergency_contact': contact.id,
})

# Create medical case
case = self.env['medical.case'].create({
    'patient_id': patient.id,
    'doctor_id': doctor.id,
    'symptoms': 'Fever, headache',
    'diagnosis': 'Viral infection',
})

# Schedule appointment
appointment = self.env['medical.appointment'].create({
    'patient_id': patient.id,
    'doctor_id': doctor.id,
    'schedule_time': '2024-04-15 10:00:00',
    'duration': 30,
})
```

### Pharmacy Management

```python
# Add medication
medication = self.env['medical.medication'].create({
    'name': 'Paracetamol',
    'code': 'MED001',
    'unit_price': 10.0,
    'stock_quantity': 1000,
})

# Create prescription
prescription = self.env['medical.prescription'].create({
    'patient_id': patient.id,
    'doctor_id': doctor.id,
    'case_id': case.id,
    'medication_lines': [(0, 0, {
        'medication_id': medication.id,
        'dosage': '500mg',
        'frequency': '3 times daily',
        'duration': '5 days',
    })],
})
```

## Development

### Model Structure

```
medical.hospital
├── medical.department
│   ├── medical.doctor
│   └── medical.patient
├── medical.case
│   ├── medical.treatment
│   └── medical.prescription
└── medical.payment
```

### Running Tests

```bash
# Unit tests
python3 odoo-bin -i futuristictech_medical -d test_db --test-enable --stop-after-init

# Test specific module
python3 odoo-bin -i futuristictech_medical -d test_db --test-enable --test-tags=/futuristictech_medical
```

### Code Quality

```bash
# Lint check
pylint --rcfile=.pylintrc ./futuristictech_medical

# Run tests with coverage
coverage run --source=./futuristictech_medical odoo-bin -i futuristictech_medical -d test_db --test-enable
coverage report
```

## API Reference

### Hospital Endpoints

```python
# GET /api/v1/hospitals
@http.route('/api/v1/hospitals', auth='user', type='json', methods=['GET'])
def get_hospitals(self, **kwargs):
    hospitals = request.env['medical.hospital'].search([])
    return hospitals.read(['name', 'registration_number'])

# POST /api/v1/hospitals
@http.route('/api/v1/hospitals', auth='user', type='json', methods=['POST'])
def create_hospital(self, **kwargs):
    return request.env['medical.hospital'].create(kwargs)

# GET /api/v1/hospitals/<id>
@http.route('/api/v1/hospitals/<int:id>', auth='user', type='json', methods=['GET'])
def get_hospital(self, id, **kwargs):
    hospital = request.env['medical.hospital'].browse(id)
    return hospital.read(['name', 'registration_number'])
```

### Patient Endpoints

```python
# GET /api/v1/patients
@http.route('/api/v1/patients', auth='user', type='json', methods=['GET'])
def get_patients(self, **kwargs):
    patients = request.env['medical.patient'].search([])
    return patients.read(['name', 'registration_number'])

# POST /api/v1/patients
@http.route('/api/v1/patients', auth='user', type='json', methods=['POST'])
def create_patient(self, **kwargs):
    return request.env['medical.patient'].create(kwargs)
```

## Support

- Documentation: [docs.futuristictech.com/medical](https://docs.futuristictech.com/medical)
- Issues: [GitHub Issues](https://github.com/futuristictech/medical/issues)
- Forum: [Odoo Community Forum](https://www.odoo.com/forum/help-1)

## License

This module is licensed under [LGPL-3.0](LICENSE)

```./odoo-bin -c odoo.conf -d futuristictech_medical -u futuristictech_medical```kw