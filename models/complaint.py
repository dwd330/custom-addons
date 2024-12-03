import requests
from odoo import models, fields, api, _
import firebase_admin
from firebase_admin import credentials, messaging
from odoo.tools.misc import file_path
from odoo.exceptions import UserError

class Complaint(models.Model):
    _name = 'complaint'
    _description = 'Customer Complaints'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True, default=lambda self: 'New')
    patient_id = fields.Many2one('res.partner', string='Patient')
    contact_phone = fields.Char(string='Contact Phone', related='patient_id.phone', tracking=True)
    contact_email = fields.Char(string='Contact Email', related='patient_id.email', tracking=True)
    agent_id = fields.Many2one('res.users', string='Agent', tracking=True)
    agent_name = fields.Char(string='Agent Name', related='agent_id.name', tracking=True)
    agent_phone = fields.Char(string='Agent Phone', related='agent_id.phone', tracking=True)
    description = fields.Text(string='Description of Complaint', tracking=True)
    date_of_create = fields.Datetime(string='Date and Time of Call', default=fields.Datetime.now, tracking=True)
    notes = fields.Text(string='Notes', tracking=True)
    state = fields.Selection([
        ('Pending', 'Pending'),
        ('In_Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ], string='State', default='Pending', tracking=True)
    type = fields.Selection([
        ('medical', 'medical'),
        ('administrative', 'administrative'),
        ('financial', 'financial'),
    ], string='type', default='financial', tracking=True)
    resolution = fields.Text(string='Resolution', tracking=True, groups='complaints.group_complaint_admin')
    schedule_follow_up = fields.Datetime(string='Schedule Follow Up', default=fields.Datetime.now, tracking=True)
    request_approval = fields.Text(string='Approval Request', readonly=True, tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('complaints.reference') or 'New'
        return super(Complaint, self).create(vals)

    def write(self, vals):
        if 'state' in vals:
            state_change_message = f"Complaint status changed to {vals['state']}"
            self.message_post(body=state_change_message)
        return super(Complaint, self).write(vals)

    def action_state_pending(self):
        self.write({'state': 'Pending'})

    def action_state_inprogress(self):
        self.write({'state': 'In_Progress'})

    def action_state_resolved(self):
        self.write({'state': 'Resolved'})

    def action_state_closed(self):
        self.write({'state': 'Closed'})





#notifcation handle:::

    def get_all_fcm_tokens(self):
        # Fetch all FCM token records
        fcm_tokens = self.env['fcm.token'].sudo().search([])
        # Extract unique tokens using a set, then convert to tuple
        token_tuple = tuple({fcm.token for fcm in fcm_tokens if fcm.token})
        return list(token_tuple)

    def action_request_permission(self):
        # Initialize Firebase only if it hasn't been initialized
        if not firebase_admin._apps:
            # Use file_open to get the correct path for static resources
            with open(file_path('complaints/static/fcm/cert.json')) as f:
                cred = credentials.Certificate(f.name)
                firebase_admin.initialize_app(cred)
                print(f"Firebase initialized with credentials at: {f.name}")  # Debug line for path checking

        # Get all registration tokens
        registration_tokens = self.get_all_fcm_tokens()
        if not registration_tokens:
            raise UserError("There are no registration tokens yet.")
        
        # Send a message to each token
        for token in registration_tokens:
            message = messaging.Message(
                notification=messaging.Notification(
                    title="odoo Requests",
                    body=f'You have a new request for approval: {self.name}'
                ),
                token=token,
                data={'complaint_name': str(self.name)},
            )
            try:
                response = messaging.send(message)
                print('Successfully sent message:', response)  # Logs each successful send
            except Exception as e:
                print(f"Failed to send message to token {token}: {e}")  # Logs error for each failed send

        # Display notification in Odoo for the user
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Information',
                'message': 'Notifications have been sent successfully.',
                'sticky': False,  # True will make the message stay until closed manually
                'type': 'info',  # Options are: info, warning, danger, success
            }
        }



