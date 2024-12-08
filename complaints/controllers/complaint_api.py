# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request, Response
import logging
import json

_logger = logging.getLogger(__name__)

class complaint_Request(http.Controller):

    @http.route('/complaints/approval_request/', auth='public', csrf=False, type='json', methods=['POST'])
    def approval_request(self, **kwargs):
        # Extract the complaint name and data to update
        response = http.request.httprequest.data
        response_str = response.decode('utf-8')
        response_dict = json.loads(response_str)
        name = response_dict.get('name')
        update_data = response_dict.get('data')

        # Ensure the complaint ID is provided
        if not name:
            return {'status': 'error', 'message': 'Complaint name is required'}

        # Search for the complaint record
        complaint = request.env['complaint'].sudo().search([('name', '=', name)], limit=1)

        if not complaint:
            return {'status': 'error', 'message': 'Complaint not found'}

        try:
            # Update the complaint record
            complaint.sudo().write(update_data)
            return {'status': 'success', 'message': 'Complaint updated successfully'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    @http.route('/complaints/approval_check/', auth='public', csrf=False, type='json', methods=['GET'])
    def approval_check(self, **kwargs):
        # Access the request data using kwargs or request.jsonrequest
        data = request.jsonrequest
        return {'status': 'success', 'data': data}

    @http.route('/complaints/create/', auth='public', csrf=False, type='json', methods=['POST'])
    def complaint_create(self, **kwargs):
        # Extract the complaint name and data to update
        response = http.request.httprequest.data
        response_str = response.decode('utf-8')
        response_dict = json.loads(response_str)['data']
        agent_id = response_dict.get('agent_id')
        description = response_dict.get('description')
        notes = response_dict.get('notes')
        type = response_dict.get('type')

        # Validate required fields
        if not description or not agent_id:
            return {'status': 'error', 'message': 'Missing required fields: name, agent_id, patient_id'}
        # Prepare data for creation
        complaint_data = {
            'create_uid':agent_id,
            'agent_id': agent_id,
            'description': description,
            'notes': notes,
            'type': type,
        }

        try:
            # Create the complaint record
            complaint = request.env['complaint'].sudo().create(complaint_data)
            return {'status': 'success', 'message': 'Complaint created successfully', 'complaint id': complaint.id,'agent_id': agent_id}
        except Exception as e:
            _logger.error(f"Error creating complaint: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/complaints/getall', auth='public', csrf=False, type='json', methods=['GET'])
    def get_all_complaints(self):
        complaints = request.env['complaint'].sudo().search([])
        complaint_list = []
        for complaint in complaints:
            complaint_list.append({
                'id': complaint.id,
                'name': complaint.name,
                'agent_id': complaint.agent_id.id,
                'agent_name': complaint.agent_id.name or "",
                'agent_phone': complaint.agent_id.phone or "",
                'patient_id': complaint.patient_id.id or "",
                'patient_name': complaint.patient_id.name or "",
                'patient_phone': complaint.patient_id.phone or "",
                'description': complaint.description or "",
                'state': complaint.state,
                'type': complaint.type,
                'resolution': complaint.resolution or "",
                'notes': complaint.notes or "",
                'date_of_create': complaint.date_of_create or "",
                'request_approval': complaint.request_approval or "",
            })
        return {'status': 'success', 'complaints': complaint_list}

