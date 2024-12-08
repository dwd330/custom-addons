# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request, Response
import logging
import json

class PermissionCheckerController(http.Controller):
    @http.route('/api/permission', type='json', auth='none', methods=['POST'], csrf=False)
    def check_permission(self, **kwargs):
        response = http.request.httprequest.data
        response_str = response.decode('utf-8')
        response_dict = json.loads(response_str)
        username = response_dict.get('username')
        if not username:
            return {'error': 'Username is required'}

        # Authenticate as admin to access user data
        env = request.env(user=1)  # user=1 is the admin user

        # Search for the user by username (login)
        user = env['res.users'].sudo().search([('login', '=', username)], limit=1)
        if not user:
            return {'error': 'User not found'}

        complaint_user_group = env.ref('complaints.group_complaint_user', raise_if_not_found=False)
        complaint_admin_group = env.ref('complaints.group_complaint_admin', raise_if_not_found=False)

        # Check if the groups exist
        if not complaint_user_group or not complaint_admin_group:
            return {'error': 'Complaint groups not found'}

        # Determine if the user has permission
        has_permission = bool(set(user.groups_id.ids) & set([complaint_user_group.id, complaint_admin_group.id]))
        if user.has_group('complaints.group_complaint_admin'):
            authorization = 'admin'
        elif user.has_group('complaints.group_complaint_user'):
            authorization = 'user'
        else:
            authorization = 'no_access'
        return {
            'username': username,
            'has_permission': has_permission,
            'authorization': authorization
        }
