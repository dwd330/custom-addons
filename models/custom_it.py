from odoo import models, api

class ITManagement(models.Model):
    _name = 'it_management'
    _description = 'Custom IT Management'


    @api.model
    def create_init_category_locations(self):
        # Define locations
        locations = [
            {'name': 'HR m09', 'emirates': 'Dubai', 'type': 'office'},
            {'name': 'marketing m01', 'emirates': 'Dubai', 'type': 'office'},
            {'name': 'marketing 202', 'emirates': 'Dubai', 'type': 'office'},
            {'name': 'vitasign 102', 'emirates': 'Dubai', 'type': 'office'},
            {'name': 'sydney medical center', 'emirates': 'Dubai', 'type': 'clinic'},
            {'name': 'nmmc medical center', 'emirates': 'Dubai', 'type': 'clinic'},
            {'name': 'arya clinic', 'emirates': 'Dubai', 'type': 'clinic'},
            {'name': 'american esthetic ', 'emirates': 'Dubai', 'type': 'clinic'},
        ]

        # Create locations if they do not exist
        for location in locations:
            if not self.env['equipment.location'].search([('name', '=', location['name'])], limit=1):
                self.env['equipment.location'].create(location)

        # Define categories
        categories = [
            {'name': 'printer'},
            {'name': 'sim'},
            {'name': 'nvr'},
            {'name': 'mobile'},
            {'name': 'computer'},
            {'name': 'network'},
        ]

        # Create categories if they do not exist
        for category in categories:
            if not self.env['maintenance.equipment.category'].search([('name', '=', category['name'])], limit=1):
                self.env['maintenance.equipment.category'].create(category)
