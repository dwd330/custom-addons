# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request, Response
import json

class LoginController(http.Controller):

    @http.route('/odoo/login', type='json', auth='public', methods=['POST'], csrf=False)
    def login(self, **post):
        # Get the raw HTTP request data
        response = http.request.httprequest.data
        response_str = response.decode('utf-8')
        response_dict = json.loads(response_str)

        # Extract the login, password, and db values
        login = response_dict.get('login')
        password = response_dict.get('password')
        db = response_dict.get('db')
        # Check for missing parameters
        if not login or not password or not db:
            return {
                'result': {'error': 'Missing login, password, or database'}
            }
        try:
            # Authenticate the user
            uid = request.session.authenticate(db, login, password)
            if uid:
                # Retrieve user information
                user = request.env['res.users'].browse(uid)

                # Reference groups
                complaint_user_group = request.env.ref('complaints.group_complaint_user', raise_if_not_found=False)
                complaint_admin_group = request.env.ref('complaints.group_complaint_admin', raise_if_not_found=False)
                # Check if the groups exist
                if not complaint_user_group or not complaint_admin_group:
                    return {'error': 'Complaint groups not found'}

                # Determine if the user has permission
                has_permission = bool(set(user.groups_id.ids) & set([complaint_user_group.id, complaint_admin_group.id]))
                if user.has_group('complaints.group_complaint_admin'):
                    userRole = 'admin'
                elif user.has_group('complaints.group_complaint_user'):
                    userRole = 'user'
                else:
                    userRole = 'no_access'


                return {
                    'result': {
                        'success': True,
                        'user_id': uid,
                        'username': user.name,
                        'login': user.login,
                        'has_permission': has_permission,
                        'userRole': userRole,
                        'session_id': request.session.sid
                    }
                }
            else:
                return {
                    'result': {'error': 'Invalid login credentials'}
                }
        except Exception as e:
            return {
                'result': {'error': str(e)}
            }
