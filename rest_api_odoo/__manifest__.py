# -*- coding: utf-8 -*-

{
    "name": "Odoo rest API",
    "version": "17.0.1.0.2",
    "category": "Tools",
    "summary": """This app helps to interact with odoo, backend with help of 
     rest api requests""",
    "description": """The odoo Rest API module allow us to connect to database 
     with the help of GET , POST , PUT and DELETE requests""",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    "depends": ['base', 'web'],
    "data": [
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
        'views/connection_api_views.xml'
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
